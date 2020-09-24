from helpers.alex import *

date = datetime.date.today().strftime('%Y-%m-%d')
state = 'TX'

def fetch(url, **kwargs):
    if 'date' not in kwargs.keys() or kwargs['date']==False:
        kwargs['date'] = date
    if 'state' not in kwargs.keys() or kwargs['state']==False:
        kwargs['state'] = state
    return(fetch_(url, **kwargs))

def run_TX(args):
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
    
    earliest_date_w_demographics = '2020-04-15'

    # Whether to read previous data from raw or existing data.csv
    from_scratch = False 

    if from_scratch:
        date_list = pd.date_range(start=earliest_date_w_demographics, end=date).astype(str).to_list()
        date_rows = []
    else:
        date_list = [date]
        date_rows = existing_df.to_dict('records')

    for row_date in date_list:
        #print(row_date)
        if row_date<'2020-05-09':
            
            # Note: Texas does not have demographic data on ALL cases;
            # The breakdown numbers apply only to the cases for which they
            # started gathering data for on or around 4/12
            sex_url = 'https://services5.arcgis.com/ACaLB9ifngzawspq/arcgis/rest/services/Demographic_Tables/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=20&cacheHint=true'
            sex_raw = fetch(sex_url, date=row_date)
            if not sex_raw:
                print(f'Could not pull data for {state}: {row_date}')
                continue

            sex_json = json.loads(sex_raw)
            sex_df = pd.DataFrame([r['attributes'] for r in sex_json['features']])
            sex_df['Sex'] = sex_df['Sex'].replace({'Pending':'Unknown'})
            sex_df['Sex'] = 'Sex_Cases [' + sex_df['Sex'] + ']'
            sex_data = sex_df.set_index('Sex')['Count_'].to_dict()

            age_url = 'https://services5.arcgis.com/ACaLB9ifngzawspq/arcgis/rest/services/Demographic_Tables/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=2000&cacheHint=true'
            age_raw = fetch(age_url, date=row_date)
            age_json = json.loads(age_raw)
            age_df = pd.DataFrame([r['attributes'] for r in age_json['features']])
            age_df['Age_Group'] = age_df['Age_Group'].str.rstrip(' years').replace('<1', '0-1')
            age_df['Age'] = 'Age_Cases [' + age_df['Age_Group'] + ']'
            age_data = age_df.set_index('Age')['Count_'].to_dict()


            race_url = 'https://services5.arcgis.com/ACaLB9ifngzawspq/arcgis/rest/services/RaceEthnicity_View/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=6&cacheHint=true'
            race_raw = fetch(race_url, date=row_date)
            race_json = json.loads(race_raw)
            race_df = pd.DataFrame([r['attributes'] for r in race_json['features']])
            race_df['Race'] = 'Race_Cases [' + race_df['Race_Ethnicity'] + ']'
            race_data = race_df.set_index('Race')['Count_'].to_dict()

            tests_url = 'https://txdshs.maps.arcgis.com/sharing/rest/content/items/ed483ecd702b4298ab01e8b9cafc8b83/data?f=json'
            tests_raw = fetch(tests_url, date=row_date)
            tests_json = json.loads(tests_raw)
            tests_str = [w for w in tests_json['widgets'] if w['name']=='Indicator (4)'][0]['defaultSettings']['middleSection']['textInfo']['text']
            tests = int(re.sub('[^0-9]','', tests_str))

            cases_url = 'https://services5.arcgis.com/ACaLB9ifngzawspq/arcgis/rest/services/COVID19County_ViewLayer/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Count_%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&cacheHint=true'
            cases_raw = fetch(cases_url, date=row_date)
            cases_json = json.loads(cases_raw)
            cases = int(cases_json['features'][0]['attributes']['value'])

            # Had bad typo; past deaths_url wasn't downloaded
            deaths_url = 'https://services5.arcgis.com/ACaLB9ifngzawspq/arcgis/rest/services/COVID19County_Death/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&cacheHint=true'
            #deaths_raw = fetch(cases_url, date=row_date)
            #deaths_json = json.loads(deaths_raw)
            #deaths = int(deaths_json['features'][0]['attributes']['value'])

            # Will fill in data from timeseries in recent spreadsheet data
            raw_xlsx = fetch('https://www.dshs.state.tx.us/coronavirus/TexasCOVID19CaseCountData.xlsx', date='2020-05-10', extension='xlsx')
            timeseries = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Trends').iloc[2:,:3]
            timeseries.columns = ['Date', 'Cases', 'Deaths']
            timeseries.Date = pd.to_datetime(timeseries.Date).astype(str)
            deaths = int(timeseries.loc[timeseries.Date==row_date, 'Deaths'])


        elif row_date=='2020-05-09':
            raw_xlsx = fetch('https://www.dshs.state.tx.us/coronavirus/TexasCOVID19CaseCountData.xlsx', date='2020-05-10', extension='xlsx')

            # Missed downloading XLSX for this date
            timeseries = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Trends').iloc[2:,:3]
            timeseries.columns = ['Date', 'Cases', 'Deaths']
            timeseries.Date = pd.to_datetime(timeseries.Date).astype(str)

            cases = int(timeseries.loc[timeseries.Date==row_date, 'Cases'])
            deaths = int(timeseries.loc[timeseries.Date==row_date, 'Deaths'])

            timeseries_tests = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Tests by day').iloc[2:38,:]
            timeseries_tests.columns = ['Date', 'Positive Rate', 'Tests']
            timeseries_tests.Date = pd.to_datetime(timeseries_tests.Date).astype(str)
            tests = int(timeseries_tests.loc[timeseries_tests.Date=='2020-05-09', 'Tests'])

            sex_data = {}
            age_data = {}
            race_data = {}

        else:
            url = 'https://www.dshs.state.tx.us/coronavirus/TexasCOVID19CaseCountData.xlsx'
            raw_xlsx = fetch(url, date=row_date, extension='xlsx')

            cases_df = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Case and Fatalities').T.set_index(0).T
            cases_df.columns = ['County', 'Cases', 'Fatalities']
            cases = int(cases_df.loc[cases_df.County=='Total', 'Cases'])
            deaths = int(cases_df.loc[cases_df.County=='Total', 'Fatalities'])

            if row_date<='2020-09-13':
                tests_df = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Tests').T.set_index(0).T
                if 'Location' not in tests_df.columns:
                    tests_df.columns = ['Location', 'Count']
                tests = int(tests_df.loc[tests_df.Location=='Total Tests', 'Count'])
            else:
                tests_df = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Tests by Day').T.set_index(0).T
                tests_df = tests_df.iloc[:-2,:5].T.set_index(1).T
                tests_df['date'] = pd.to_datetime(tests_df['Lab Reported Date']).dt.date
                tests = tests_df['Test Results'].sum()

            age_cases_df = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Cases by Age Group').T.set_index(0).T.iloc[:13,:]
            age_cases_df.columns = ['Group', 'Counts', '%']
            age_cases_df.Group = age_cases_df.Group.str.rstrip(' years').replace({'<1': '0-1'})
            age_cases_df['Colnames'] = 'Age_Cases [' + age_cases_df.Group + ']'
            age_cases_data = age_cases_df.set_index('Colnames')['Counts'].to_dict()

            age_deaths_df = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Fatalities by Age Group').T.set_index(0).T.iloc[:13,:]
            age_deaths_df.columns = ['Group', 'Counts', '%']
            age_deaths_df.Group = age_deaths_df.Group.str.rstrip(' years').replace({'<1': '0-1'})
            age_deaths_df['Colnames'] = 'Age_Deaths [' + age_deaths_df.Group + ']'
            age_deaths_data = age_deaths_df.set_index('Colnames')['Counts'].to_dict()

            age_data = {**age_cases_data, **age_deaths_data}

            race_cases_df = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Cases by RaceEthnicity').T.set_index(0).T.iloc[:6,:]
            race_cases_df.columns = ['Group', 'Counts', '%']
            race_cases_df['Colnames'] = 'Race_Cases [' + race_cases_df.Group + ']'
            race_cases_data = race_cases_df.set_index('Colnames')['Counts'].to_dict()

            race_deaths_df = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Fatalities by Race-Ethnicity').T.set_index(0).T.iloc[:6,:]
            race_deaths_df.columns = ['Group', 'Counts', '%']
            race_deaths_df['Colnames'] = 'Race_Deaths [' + race_deaths_df.Group + ']'
            race_deaths_data = race_deaths_df.set_index('Colnames')['Counts'].to_dict()

            race_data = {**race_cases_data, **race_deaths_data}

            sex_cases_df = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Cases by Gender').T.set_index(0).T.iloc[:3,:]
            sex_cases_df.columns = ['Group', 'Counts', '%']
            sex_cases_df['Colnames'] = 'Sex_Cases [' + sex_cases_df.Group + ']'
            sex_cases_data = sex_cases_df.set_index('Colnames')['Counts'].to_dict()

            sex_deaths_df = pd.read_excel(raw_xlsx, engine='xlrd', sheet_name='Fatalities by Gender').T.set_index(0).T.iloc[:3,:]
            sex_deaths_df.columns = ['Group', 'Counts', '%']
            sex_deaths_df['Colnames'] = 'Sex_Deaths [' + sex_deaths_df.Group + ']'
            sex_deaths_data = sex_deaths_df.set_index('Colnames')['Counts'].to_dict()

            sex_data = {**sex_cases_data, **sex_deaths_data}


        pullTime = get_pull_time(existing_df, row_date)
         
        row_data = {
            'state': 'Texas',
            'stateAbbrev': 'TX',
            'date': row_date,
            'Cases': cases,
            'Deaths': deaths,
            'Tests': tests,
            **sex_data,
            **age_data,
            **race_data,
            'pullTime': pullTime
        }

        existing_dates = [r['date'] for r in date_rows]
        if row_date in existing_dates:
            idx = existing_dates.index(row_date)
            date_rows[idx] = row_data
        else:
            date_rows.append(row_data)


    # Save data
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    timeseries = pd.DataFrame(date_rows)
    timeseries['date'] = pd.to_datetime(timeseries['date']).dt.date
    timeseries = timeseries.sort_values('date')
    timeseries.to_csv(csv_location, index=False)

if __name__=='__main__':
    run_TX({})
    

