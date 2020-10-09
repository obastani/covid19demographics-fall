from helpers.alex import *

date = datetime.date.today().strftime('%Y-%m-%d')
state = 'PA'

def fetch(url, **kwargs):
    if 'date' not in kwargs.keys() or kwargs['date']==False:
        kwargs['date'] = date
    if 'state' not in kwargs.keys() or kwargs['state']==False:
        kwargs['state'] = state
    return(fetch_(url, **kwargs))

def get_data_from_url(url, data_type=float, index_key=False):
    r = fetch(url)
    data = json.loads(r)
    if data_type==float:
        output = data['features'][0]['attributes']['value']
    elif data_type==dict and index_key!='all':
        features = data['features']
        output = {}
        for f in features:
            if not index_key:
                index_key = [k for k in f['attributes'].keys() if k!='value'][0]
            key = f['attributes'][index_key]
            if 'value' in f['attributes'].keys():
                val = f['attributes']['value']
            elif 'Count_' in f['attributes'].keys():
                val = f['attributes']['Count_']
            else:
                raise Exception(f'JSON has new format with unexpected key: {f["attributes"]}')
            output[key] = val
    elif data_type==dict:
        if len(data['features'])==1:
            output = data['features'][0]['attributes']
        else:
            output = [f['attributes'] for f in data['features']]
    return(output)


def run_PA(args):
    # Load existing data
    data_folder = Path(project_root, state, 'data')
    csv_location = Path(data_folder, 'data.csv')
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    if Path(data_folder, 'data.csv').exists():
        existing_df = pd.read_csv(csv_location)
    else:
        existing_df = pd.DataFrame([])


    # Fetch raw data
    
    # Get date to fetch
    if 'day' in args:
        date_obj = datetime.date(args['year'], args['month'], args['day'])
        date = date_obj.strftime('%Y-%m-%d')
    else:
        # If none provided, assume today 
        if datetime.datetime.now().hour >= 15:
            date_obj = datetime.date.today() 
        # Unless before 3pm, then assume yesterday
        else:
            date_obj = datetime.date.today() - datetime.timedelta(days=1)
        date = date_obj.strftime('%Y-%m-%d')

    
    earliest_date_w_demographics = '2020-03-27'

    # Whether to read previous data from raw or existing data.csv
    from_scratch = False 

    if from_scratch:
        date_list = pd.date_range(start=earliest_date_w_demographics, end=date).astype(str).to_list()
        date_rows = []
    else:
        date_list = [date]
        existing_df = pd.read_csv(csv_location)
        date_rows = existing_df.to_dict('records')

    for row_date in date_list:
        
        # Fetch historical data from https://github.com/lazd/coronadatascraper-cache
        if row_date=='2020-03-27':
            row_date_obj = dparser.parse(row_date)
            cds_date = f'{row_date_obj.year}-{row_date_obj.month}-{row_date_obj.day}'
            cds_cache_url = f'https://github.com/lazd/coronadatascraper-cache/raw/master/{cds_date}/6847ef86804ff0c3c03f31ca00d7eb6d.html'
            raw = fetch(cds_cache_url, date=row_date, time_travel=True)
        elif row_date<'2020-06-10':
            url = 'https://www.health.pa.gov/topics/disease/coronavirus/Pages/Cases.aspx'
            raw = fetch(url, date=row_date)

            if not raw:
                print(f'Could not pull data for {state}: {row_date}')
                continue

            # Process raw data 
            tables = pd.read_html(raw)
            soup = BeautifulSoup(raw, 'html.parser')

            # Get tested and case counts
            counts_df = tables[0]
            counts_df = counts_df.apply(lambda column: column.str.strip(u'\u200b'), axis=0) 
            counts_df = counts_df.T.set_index(0).T
            if row_date<'2020-04-22':
                total_cases = int(counts_df['Positive'])
                tested_count = int(counts_df[['Positive','Negative']].astype(int).sum(1))
                deaths = int(counts_df['Deaths'])

                cases_data = {}
                cases_data['Cases'] = total_cases
                cases_data['Tested'] = tested_count
                cases_data['Deaths'] = deaths

            else:
                total_cases = int(counts_df['Total Cases*'])
                counts_df = counts_df.rename(columns={'Negative**': 'Negative'})
                tested_count = int(counts_df[['Total Cases*','Negative']].astype(int).sum(1))
                deaths_col = [c for c in counts_df.columns if 'Death' in c][0]
                deaths = int(counts_df[deaths_col])

                cases_data = {}
                if row_date<'2020-05-22':
                    cases_search = soup.find('strong', text=re.compile('​Confirmed Cases'))
                    if cases_search:
                        cases_html = cases_search.find_parent('table')
                        cases_df = pd.read_html(str(cases_html))[0]
                        cases_df = cases_df.apply(lambda column: column.str.strip('\u200b'))
                        cases_df = cases_df.iloc[1:,:]
                        cases_df.iloc[0,:] = cases_df.iloc[0,:].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(int)
                        cases_df.columns = ['Cases_Confirmed', 'Cases_Probable', 'Deaths_Confirmed', 'Deaths_Probable']
                        cases_data = cases_df.T[1].to_dict()

                cases_data['Cases'] = total_cases
                cases_data['Tested'] = tested_count
                cases_data['Deaths'] = deaths


            # Get age distribution of cases
            age_html = soup.find('strong', text=re.compile('Age Range')).find_parent('table')
            age_df = pd.read_html(str(age_html))[0]
            age_df = age_df.apply(lambda column: column.str.strip('\u200b'))
            age_df = age_df.drop(0)
            age_df.columns = ['Age', 'Percent']
            age_df['Age'] = 'Age ['+ age_df['Age'] +']'
            age_df.loc[age_df['Percent'].str.contains('< 1'), 'Percent'] = '0'
            age_df['Percent'] = age_df['Percent'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
            age_df['Counts'] = (age_df['Percent']*total_cases).astype(int)
            age_data = age_df[['Age','Counts']].set_index('Age')['Counts'].to_dict()

            # Get total hospitalizations
            hosp_age_data = {}
            hosp = False
            soup = BeautifulSoup(raw, 'html.parser')
            h4s = [s.get_text().strip() for s in soup.find_all('h4')]
            hosp_idx = [i for i,s in enumerate(h4s) if s.startswith('Hospitalization')][0]
            hosp_title_tag = soup.find_all('h4')[hosp_idx]
            hosp_total_tags = hosp_title_tag.find_next('p').find_all('strong')

            if len(hosp_total_tags)>1:
                hosp = int(hosp_total_tags[1].get_text().strip())

            elif row_date>='2020-04-16':
                hosp_url = "https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Adam_County_Summary_V3/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22COVID_19_Patient_Counts_Total_2%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true"

                if row_date>='2020-04-22':
                    hosp_url = "https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Adam_County_Summary_Table_v4/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22COVID_19_Patient_Counts_Total_2%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true"
                headers = {
                    "accept": "*/*",
                    "accept-language": "en-US,en;q=0.9",
                    "if-modified-since": "Fri, 17 Apr 2020 00:46:32 GMT",
                    "if-none-match": "sd6612_-823333576",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    "referer": "https://www.arcgis.com/apps/opsdashboard/index.html"
                }
                hosp_raw = fetch(hosp_url, headers=headers)
                hosp_json = json.loads(hosp_raw)
                if 'features' in hosp_json.keys():
                    hosp = int(hosp_json['features'][0]['attributes']['value'])
                else:
                    hosp = False

            if hosp:
                # Get age distribution of hospitalizations
                hosp_age_df = pd.read_html(str(hosp_title_tag.find_next('table')))[0]
                hosp_age_df = hosp_age_df.apply(lambda column: column.str.strip('\u200b'))
                hosp_age_df = hosp_age_df.drop(0)
                hosp_age_df.columns = ['Age', 'Percent']
                hosp_age_df['Age'] = 'Hospitalized_Age ['+ hosp_age_df['Age'] +']'
                hosp_age_df.loc[hosp_age_df['Percent'].str.contains('< 1'), 'Percent'] = '0'
                hosp_age_df['Percent'] = hosp_age_df['Percent'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                hosp_age_df['Counts'] = (hosp_age_df['Percent']*hosp).astype(int)
                hosp_age_data = hosp_age_df[['Age','Counts']].set_index('Age')['Counts'].to_dict()
                #print(hosp_age_df)
                
            else:
                hosp_age_data = {}

            sex_search = soup.find('strong', text=re.compile('Sex'))
            if sex_search:
                sex_html = sex_search.find_parent('table')
                sex_df = pd.read_html(str(sex_html))[0].T.set_index(0).T
                sex_df = sex_df.replace({'Not reported': 'Unknown'})
                sex_df = sex_df.rename(columns={'Positive Cases*':'Positive Cases'})
                sex_df['Colnames'] = 'Sex_Cases [' + sex_df['Sex'] + ']'
                sex_cases_data = sex_df.set_index('Colnames')['Positive Cases'].to_dict()
                if 'Deaths' in sex_df.columns:
                    sex_df['Colnames'] = 'Sex_Deaths [' + sex_df['Sex'] + ']'
                    sex_deaths_data = sex_df.set_index('Colnames')['Deaths'].to_dict()
                else:
                    sex_deaths_data = {}

                sex_data = {
                    **sex_cases_data,
                    **sex_deaths_data
                }
            else:
                sex_data = {}

            race_search = soup.find('strong', text=re.compile('Race'))
            if race_search:
                race_html = race_search.find_parent('table')
                race_df = pd.read_html(str(race_html))[0].T.set_index(0).T
                race_df['Colnames'] = 'Race_Cases [' + race_df['Race'] + ']'
                race_cases_data = race_df.set_index('Colnames')['Positive Cases'].to_dict()
                if 'Deaths' in race_df.columns:
                    race_df['Colnames'] = 'Race_Deaths [' + race_df['Race'] + ']'
                    race_deaths_data = race_df.set_index('Colnames')['Deaths'].to_dict()
                else:
                    race_deaths_data = {}
                    
                race_data = {
                    **race_cases_data,
                    **race_deaths_data
                }
            else:
                race_data = {}

        else:
            if row_date<'2020-10-07':

                cases_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Pennsylvania_Public_COVID19_Dashboard_Data/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Confirmed%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
                probable_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Pennsylvania_Public_COVID19_Dashboard_Data/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Probable%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
                negative_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Pennsylvania_Public_COVID19_Dashboard_Data/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Negative%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
                deaths_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Pennsylvania_Public_COVID19_Dashboard_Data/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
                hosp_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Adam_County_Summary_Table_v5/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22numc19hosppats%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'

                confirmed_cases = get_data_from_url(cases_url, data_type=float)
                probable_cases = get_data_from_url(probable_url, data_type=float)
                negative = get_data_from_url(negative_url, data_type=float)
                deaths = get_data_from_url(deaths_url, data_type=float)
                hosp = get_data_from_url(hosp_url, data_type=float)

                cases_data = {
                    'Cases': confirmed_cases + probable_cases,
                    'ProbableCases': probable_cases,
                    'Tested': confirmed_cases + negative,
                    'Deaths': deaths
                }

            else:
                totals_url = 'https://services1.arcgis.com/Nifc7wlHaBPig3Q3/arcgis/rest/services/COVID_PA_Counties/FeatureServer/0/query?f=json&where=County%3D%27Pennsylvania%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=1&resultType=standard&cacheHint=true'
                totals_dict = get_data_from_url(totals_url, data_type=dict, index_key='all')

                cases_data = {
                    'Cases': totals_dict['Confirmed'] + totals_dict['Probable'],
                    'ProbableCases': totals_dict['Probable'],
                    'Tested': totals_dict['Confirmed'] + totals_dict['Negative'],
                    'Deaths': totals_dict['Deaths']
                }

                hosp_url = 'https://services1.arcgis.com/Nifc7wlHaBPig3Q3/arcgis/rest/services/covid_hosp_single_day/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22covid_patients%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
                hosp = get_data_from_url(hosp_url, data_type=float)


            if row_date<'2020-10-07':
                age_cases_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Pennsylvania_Public_COVID19_Dashboard_Data/FeatureServer/2/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Age_Range&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Cases%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            else:
                age_cases_url = 'https://services1.arcgis.com/Nifc7wlHaBPig3Q3/arcgis/rest/services/AgeCases/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Age_Range&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Cases%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            age_cases_dict = get_data_from_url(age_cases_url, data_type=dict)
            age_cases_series = pd.Series(age_cases_dict).fillna(0).astype(int)
            age_cases_series.index = 'Age_Cases [' + pd.Series(age_cases_series.index) + ']'
            age_cases_data = age_cases_series.to_dict()

            if row_date<'2020-06-14':
                age_deaths_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/deathsage/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Age_Range&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Number_of_Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            elif row_date<'2020-10-07':
                age_deaths_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/deathsagenew/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Sorting%20asc&resultOffset=0&resultRecordCount=32000&resultType=standard&cacheHint=true'
            else:
                age_deaths_url = 'https://services1.arcgis.com/Nifc7wlHaBPig3Q3/arcgis/rest/services/Deaths_Age/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Sorting%20asc&resultOffset=0&resultRecordCount=32000&resultType=standard&cacheHint=true'
            age_deaths_dict = get_data_from_url(age_deaths_url, data_type=dict, index_key='Age_Range')
            age_deaths_series = pd.Series(age_deaths_dict).fillna(0).astype(int)
            #print(age_deaths_series)
            age_deaths_series.index = 'Age_Deaths [' + pd.Series(age_deaths_series.index) + ']'
            age_deaths_data = age_deaths_series.to_dict()

            age_data = {
                **age_cases_data,
                **age_deaths_data
            }

            if row_date<'2020-10-07':
                sex_cases_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Pennsylvania_Public_COVID19_Dashboard_Data/FeatureServer/3/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Gender&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Positive%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            else:
                sex_cases_url = 'https://services1.arcgis.com/Nifc7wlHaBPig3Q3/arcgis/rest/services/gendercases/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Gender&orderByFields=value%20desc&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Positive%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            sex_cases_dict = get_data_from_url(sex_cases_url, data_type=dict)
            sex_cases_series = pd.Series(sex_cases_dict).fillna(0).astype(int)
            sex_cases_series.index = 'Sex_Cases [' + pd.Series(sex_cases_series.index) + ']'
            sex_cases_data = sex_cases_series.to_dict()

            if row_date<'2020-10-07':
                sex_deaths_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/deathgender/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Gender&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22F__of_Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            else:
                sex_deaths_url = 'https://services1.arcgis.com/Nifc7wlHaBPig3Q3/arcgis/rest/services/Death_Gender/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Gender&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22F__of_Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            sex_deaths_dict = get_data_from_url(sex_deaths_url, data_type=dict)
            sex_deaths_series = pd.Series(sex_deaths_dict).fillna(0).astype(int)
            sex_deaths_series.index = 'Sex_Deaths [' + pd.Series(sex_deaths_series.index) + ']'
            sex_deaths_data = sex_deaths_series.to_dict()

            sex_data = {
                **sex_cases_data,
                **sex_deaths_data
            }

            if row_date<'2020-10-07':
                race_cases_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Pennsylvania_Public_COVID19_Dashboard_Data/FeatureServer/8/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Race&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Positive_Cases%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            else:
                race_cases_url = 'https://services1.arcgis.com/Nifc7wlHaBPig3Q3/arcgis/rest/services/racedata/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Race&orderByFields=value%20desc&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Positive_Cases%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            race_cases_dict = get_data_from_url(race_cases_url, data_type=dict)
            race_cases_series = pd.Series(race_cases_dict).fillna(0).astype(int)
            race_cases_series = race_cases_series.reset_index().replace({
                'African American': 'African American/Black',
                'Not Reported': 'Not reported',
                'Black': 'African American/Black',
                'Unknown': 'Not reported'
            }).set_index('index')
            race_cases_series.index = 'Race_Cases [' + pd.Series(race_cases_series.index) + ']'
            race_cases_data = race_cases_series.to_dict()[0]

            #print(race_cases_data)

            if row_date<'2020-10-07':
                race_death_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/deathrace/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Race&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            else:
                race_death_url = 'https://services1.arcgis.com/Nifc7wlHaBPig3Q3/arcgis/rest/services/Death_Race/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Race&orderByFields=value%20desc&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            race_death_dict = get_data_from_url(race_death_url, data_type=dict)
            race_death_series = pd.Series(race_death_dict).fillna(0).astype(int)
            race_death_series = race_death_series.reset_index().replace({
                'African American': 'African American/Black',
                'Not Reported': 'Not reported',
                'Black': 'African American/Black',
                'Unknown': 'Not reported'
            }).set_index('index')
            race_death_series.index = 'Race_Deaths [' + pd.Series(race_death_series.index) + ']'
            race_death_data = race_death_series.to_dict()[0]

            #print(race_death_data)

            if row_date<'2020-10-07':
                eth_cases_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/Pennsylvania_Public_COVID19_Dashboard_Data/FeatureServer/5/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Ethnicity&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Cases%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true' 
            else:
                eth_cases_url = 'https://services1.arcgis.com/Nifc7wlHaBPig3Q3/arcgis/rest/services/ethniccases/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Ethnicity&orderByFields=value%20desc&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Cases%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            eth_cases_dict = get_data_from_url(eth_cases_url, data_type=dict)
            eth_cases_series = pd.Series(eth_cases_dict).fillna(0).astype(int)
            eth_cases_series.index = 'Ethnicity_Cases [' + pd.Series(eth_cases_series.index) + ']'
            eth_cases_data = eth_cases_series.to_dict()

            if row_date<'2020-10-07':
                eth_deaths_url = 'https://services2.arcgis.com/xtuWQvb2YQnp0z3F/arcgis/rest/services/deathethnicity/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Ethnicity&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22F__of_Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            else:
                eth_deaths_url = 'https://services1.arcgis.com/Nifc7wlHaBPig3Q3/arcgis/rest/services/Death_Ethnicity/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Ethnicity&orderByFields=value%20desc&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22F__of_Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
            eth_deaths_dict = get_data_from_url(eth_deaths_url, data_type=dict)
            eth_deaths_series = pd.Series(eth_deaths_dict).fillna(0).astype(int)
            eth_deaths_series.index = 'Ethnicity_Cases [' + pd.Series(eth_deaths_series.index) + ']'
            eth_deaths_data = eth_deaths_series.to_dict()

            race_data = {
                **race_cases_data,
                **race_death_data,
                **eth_cases_data,
                **eth_deaths_data
            }

            hosp_age_data = {}


            
        pullTime = get_pull_time(existing_df, row_date)
            
        row_data = {
            'state': 'Pennsylvania',
            'stateAbbrev': 'PA',
            'date': row_date,
            **cases_data,
            **age_data,
            **sex_data,
            **race_data
        }
        if hosp:
            row_data = {
                **row_data,
                'Hospitalizations': hosp,
                **hosp_age_data
            }

        row_data['pullTime'] = pullTime
        

        existing_dates = [r['date'] for r in date_rows]
        if row_date in existing_dates:
            idx = existing_dates.index(row_date)
            date_rows[idx] = row_data
        else:
            date_rows.append(row_data)

    timeseries = pd.DataFrame(date_rows)
    #timeseries = timeseries[row_data.keys()]
    timeseries.to_csv(csv_location, index=False)

if __name__=='__main__':
    run_PA({})
    

