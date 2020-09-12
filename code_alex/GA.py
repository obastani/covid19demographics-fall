from helpers.alex import *

date = datetime.date.today().strftime('%Y-%m-%d')
state = 'GA'

def fetch(url, **kwargs):
    if 'date' not in kwargs.keys() or kwargs['date']==False:
        kwargs['date'] = date
    if 'state' not in kwargs.keys() or kwargs['state']==False:
        kwargs['state'] = state
    return(fetch_(url, **kwargs))

def run_GA(args):
    # Load existing data
    data_folder = Path(project_root, state, 'data')
    csv_location = Path(data_folder, 'data.csv')
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    if Path(data_folder, 'data.csv').exists():
        existing_df = pd.read_csv(csv_location)
    else:
        existing_df = pd.DataFrame([])


    # Fetch new data

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


    earliest_date_w_demographics = '2020-03-14'

    # Whether to fetch current date, re-do all from raw data, or backfill with Wayback
    run_mode =  'normal' # normal, from scratch, backfill

    if run_mode == 'from scratch':

        # Prior to 3/28, Georgia posted demographic data in images
        # I (Alex) manually read the data off these images from 
        # the Wayback Machine and saved them in GeorgiaHistorical_03-14_03-27.csv
        # After 3/28, we started scraping the iFrame Georgia used to 
        # embed/generate their demographic visualizations.
        historical_csv = Path(project_root, state, 'raw', 'GeorgiaHistorical_03-14_03-27.csv')
        historical_df = pd.read_csv(historical_csv)
        historical_df['pullTime'] = f'{datetime.datetime(2020,3,30,10,0,0)}'
        historical_df['state'] = 'Georgia'
        historical_df['stateAbbrev'] = 'GA'
        historical_rows = list(historical_df.T.to_dict().values())

        # Fetch raw data
        earliest_date_w_demographics = '2020-03-28'
        date_list = pd.date_range(start=earliest_date_w_demographics, end=date).astype(str).to_list()
        date_rows = historical_rows

    elif run_mode == 'backfill':
        existing_df = pd.read_csv(csv_location)
        date_rows = existing_df.to_dict('records')

        all_dates = pd.date_range(start=earliest_date_w_demographics, end=date).astype(str).to_list()
        fetched_dates = [r['date'] for r in date_rows]
        missing_dates = [d for d in all_dates if d not in fetched_dates]
        date_list = missing_dates
        if len(date_list)==0:
            print('No missing dates!')

        #date_list = pd.date_range(start='2020-06-02', end=date).astype(str).to_list()

    else:
        date_list = [date]
        existing_df = pd.read_csv(csv_location)
        date_rows = existing_df.to_dict('records')


    for row_date in date_list:

        # Same URL every day (so far)
        if row_date<'2020-05-18':
            url = 'https://d20s4vd27d0hk0.cloudfront.net/?initialWidth=746&childId=covid19dashdph&parentTitle=COVID-19%20Daily%20Status%20Report%20%7C%20Georgia%20Department%20of%20Public%20Health&parentUrl=https%3A%2F%2Fdph.georgia.gov%2Fcovid-19-daily-status-report'
            raw = fetch(url, date=row_date)
            if not raw:
                print(f'Could not pull data for {state}: {row_date}')
                continue

            soup = BeautifulSoup(raw, 'html.parser')                                                                                                     

            #print(row_date)
            totals_html = soup.find('td', text=re.compile('COVID\-19 Confirmed Cases:')).find_parent('table')
            totals = pd.read_html(str(totals_html))[0]
            total_cases = int(totals.loc[totals[0]=='Total',1].iloc[0].split(' ')[0])
            hosp = int(totals.loc[totals[0]=='Hospitalized',1].iloc[0].split('(')[0].strip())
            deaths = int(totals.loc[totals[0]=='Deaths',1].iloc[0].split('(')[0].strip())

            tests_html = soup.find('td', text=re.compile('Total Tests')).find_parent('table')
            tests_df = pd.read_html(str(tests_html))[0]
            tests_df = tests_df.T.set_index(0).T
            tested_count = tests_df['Total Tests'].astype(int).sum()

            # Extract age data
            pattern = r'var cage=(.+?)var c'
            matches = re.findall(pattern, raw, re.MULTILINE | re.DOTALL)
            assert len(matches)==1, "Problem with regex looking for GA's age distribution data."
            age_json = dict(hjson.loads(matches[0]))
            data_points = age_json['chart']['data'][0]['dataPoints']
            age_rows = [[row['name'], row['y']] for row in data_points]

            age_df = pd.DataFrame(age_rows, columns=['Age', 'Percent'])
            age_df['Percent'] = age_df['Percent']/100
            age_df['Counts'] = np.round(age_df['Percent']*total_cases).astype(int)
            age_df = age_df.replace({'UNK':'Unknown'})
            age_df['Age'] = age_df['Age'].str.strip()
            age_df['Age'] = 'Age_Cases ['+ age_df['Age'] +']'
            age_df[['Age', 'Counts']]

            age_data = age_df[['Age', 'Counts']].set_index('Age')['Counts'].to_dict()


            # Extract gender data
            pattern = r'var cgender=(.+?)var c'
            matches = re.findall(pattern, raw, re.MULTILINE | re.DOTALL)
            assert len(matches)==1, "Problem with regex looking for GA's sex distribution data."
            sex_json = dict(hjson.loads(matches[0]))
            data_points = sex_json['chart']['data'][0]['dataPoints']
            sex_rows = [[row['name'], row['y']] for row in data_points]
            sex_df = pd.DataFrame(sex_rows, columns=['Name', 'Percent'])
            sex_df['Percent'] = sex_df['Percent']/100
            sex_df['Value'] = np.round(sex_df['Percent']*total_cases).astype(int)
            unknown = [g for g in sex_df['Name'] if g not in ['Male','Female']]
            sex_df = sex_df.replace({k: 'Unknown' for k in unknown})
            sex_df['Name'] = 'Sex_Cases [' + sex_df['Name'] + ']'
            sex_data = sex_df[['Name', 'Value']].set_index('Name')['Value'].to_dict()

            # Race data starting 4/8
            race_search = soup.find('td', text=re.compile('Race'))
            if race_search:
                race_html = race_search.find_parent('table')
                race_eth_df = pd.read_html(str(race_html))[0].T.set_index(0).T
                has_deaths = 'Deaths' in race_eth_df.columns
                if not has_deaths:
                    summarize_cols = ['Cases']
                else:
                    summarize_cols = ['Cases', 'Deaths']
                race_eth_df[summarize_cols] = race_eth_df[summarize_cols].astype(int)
                race_df = race_eth_df.groupby('Race')[summarize_cols].sum().reset_index()
                race_df = race_df.replace({
                    'Black Or African American': 'African-American/Black',
                    'American Indian/Native American': 'American Indian/Alaska Native'
                })

                eth_df = race_eth_df.groupby('Ethnicity')[summarize_cols].sum().reset_index()

                race_df['Colnames'] = 'Race_Cases [' + race_df['Race'] + ']'
                race_cases_data = race_df.set_index('Colnames')['Cases'].to_dict()
                eth_df['Colnames'] = 'Ethnicity_Cases [' + eth_df['Ethnicity'] + ']'
                eth_cases_data = eth_df.set_index('Colnames')['Cases'].to_dict()

                race_data = {
                    **race_cases_data,
                    **eth_cases_data
                }

                if has_deaths:
                    race_df['Colnames'] = 'Race_Deaths [' + race_df['Race'] + ']'
                    race_deaths_data = race_df.set_index('Colnames')['Deaths'].to_dict()
                    eth_df['Colnames'] = 'Ethnicity_Deaths [' + eth_df['Ethnicity'] + ']'
                    eth_deaths_data = eth_df.set_index('Colnames')['Deaths'].to_dict()

                    race_data = {
                        **race_data,
                        **race_deaths_data,
                        **eth_deaths_data
                    }
                """
                elif 'var crace=' in raw:
                    pattern = r'var crace=(.+?)var c'
                    matches = re.findall(pattern, raw, re.MULTILINE | re.DOTALL)
                    assert len(matches)==1, "Problem with regex looking for GA's race distribution data."
                    race_json = dict(hjson.loads(matches[0]))
                    data_points = race_json['chart']['data'][0]['dataPoints']
                    race_rows = [[row['name'], row['y']] for row in data_points]
                    race_df = pd.DataFrame(race_rows, columns=['Name', 'Percent'])
                    race_df['Percent'] = race_df['Percent']/100
                    #race_df['Name'] = 'Race [' + race_df['Name'].str.capitalize() + ']'
                    race_df['Name'] = 'Race_Cases [' + race_df['Name'] + ']'
                    race_df['Value'] = np.round(race_df['Percent']*total_cases).astype(int)
                    race_data = race_df[['Name', 'Value']].set_index('Name')['Value'].to_dict()
                """

            else:
                race_data = {}

            # Aggregate

            row_data = {
                'state': 'Georgia',
                'stateAbbrev': 'GA',
                'date': row_date,
                'Hospitalizations': hosp,
                'Deaths': deaths,
                'Cases': total_cases,
                'Tested': tested_count,
                **age_data,
                **sex_data,
                **race_data,
                'pullTime': pullTime
            }

        # GA changed main report on 5/11; they maintained the old report until 7/13
        # Starting on 6/2, I switched the data collection from the old report to the
        # new report.
        elif row_date>='2020-06-02':
            url = 'https://ga-covid19.ondemand.sas.com/static/js/main.js'

            if run_mode=='backfill':
                if row_date<='2020-06-28':
                    time.sleep(1)
                    url = f'https://github.com/obastani/covid19demographics/blob/master/raw/GA/GA_{row_date}_gacovid19ondemandsascoms_q23tvCGFUSErig?raw=true'
                    print(url)
                    raw = fetch(url, date=row_date, time_travel=True, save=False)

                else:
                    time.sleep(1)
                    print(f'Filling in missing historical date: {row_date}')
                    raw = fetch(url, date=row_date, time_travel='wayback')

            else:
                raw = fetch(url, date=row_date, time_travel=True, save=False)

            if not raw:
                print(f'Could not pull data for {state}: {row_date}')
                continue

            # Extract data from JSON
            splits = raw.split(",function(t){t.exports=JSON.parse('")


            totals_dict = False
            demog_df = False

            for split in splits:
                try:
                    JSON = json.loads(split[:-3])
                except:
                    continue
                    
                if type(JSON)!=list:
                    continue
                    
                if sorted(JSON[0].keys()) == ['confirmed_covid', 'deaths', 'hospitalization', 'icu', 'total_tests']:
                    totals_dict = JSON[0]
                    
                elif sorted(JSON[0].keys()) == [
                    'age_group',
                    'county_name',
                    'deaths',
                    'ethnicity',
                    'hospitalization',
                    'positives',
                    'race',
                    'sex'
                ]:
                    demog_df = pd.DataFrame(JSON)
                    
                    
            if not totals_dict:
                raise Exception('Could not find totals_dict')
                
            if type(demog_df)==bool:
                raise Exception('Could not find demog_df')
                

            totals = pd.Series(totals_dict).rename({
                'total_tests': 'Tested',
                'confirmed_covid': 'Cases',
                'hospitalization': 'Hospitalizations',
                'deaths': 'Deaths',
                'icu': 'ICU'
            }).to_dict()

            demog_df = demog_df.rename(columns={
                'age_group': 'Age',
                'ethnicity': 'Ethnicity',
                'race': 'Race',
                'sex': 'Sex',
                'positives': 'Cases',
                'deaths': 'Deaths',
                'hospitalization': 'Hospitalizations'
            }).replace({
                '80 & Older': '80+',
                '<1': '0-1',
                'Missing/Unknown': 'Unknown'
            })

            row_data = {
                'state': 'Georgia',
                'stateAbbrev': 'GA',
                'date': row_date,
                **totals
            }
            for breakdown in ['Age', 'Ethnicity', 'Race']:
                for outcome in ['Cases', 'Deaths', 'Hospitalizations']:
                    grouped = demog_df.groupby(breakdown).sum()
                    values = grouped[outcome]
                    values.index = [v.replace("/ ", "/") for v in values.index]
                    values.index = [f'{breakdown}_{outcome} [{v}]' for v in values.index]
                    row_data = {
                        **row_data,
                        **values
                    }
            row_data['pullTime'] = get_pull_time(existing_df, row_date)
        
        
        existing_dates = [r['date'] for r in date_rows]
        if row_date in existing_dates:
            print(f'Overwriting data for date: {row_date}')
            idx = existing_dates.index(row_date)
            date_rows[idx] = row_data
        else:
            date_rows.append(row_data)

    # Save data
    timeseries = pd.DataFrame(date_rows)
    timeseries = timeseries.sort_values('date')
    timeseries.to_csv(csv_location, index=False)

if __name__=='__main__':
    run_GA({})
    

