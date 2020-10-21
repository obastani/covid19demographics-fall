from helpers.alex import *

date = datetime.date.today().strftime('%Y-%m-%d')
state = 'MN'

def fetch(url, **kwargs):
    if 'date' not in kwargs.keys() or kwargs['date']==False:
        kwargs['date'] = date
    if 'state' not in kwargs.keys() or kwargs['state']==False:
        kwargs['state'] = state
    return(fetch_(url, **kwargs))

def run_MN(args):
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
        # If args dictionary passed, use that date
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

    earliest_date_w_demographics = '2020-04-06'
    
    # Whether to fetch current date, re-do all from raw data, or backfill with Wayback
    run_mode =  'normal'# normal, from scratch, backfill

    if run_mode == 'from scratch':
        date_list = pd.date_range(start=earliest_date_w_demographics, end=date).astype(str).to_list()
        date_rows = []
    elif run_mode == 'backfill':
        existing_df = pd.read_csv(csv_location)
        date_rows = existing_df.to_dict('records')

        all_dates = pd.date_range(start=earliest_date_w_demographics, end=date).astype(str).to_list()
        fetched_dates = [r['date'] for r in date_rows]
        missing_dates = [d for d in all_dates if d not in fetched_dates]
        date_list = missing_dates
        if len(date_list)==0:
            print('No missing dates!')
    else:
        date_list = [date]
        existing_df = pd.read_csv(csv_location)
        date_rows = existing_df.to_dict('records')

    for row_date in date_list:
        #print(row_date)
        url = 'https://www.health.state.mn.us/diseases/coronavirus/situation.html'

        if run_mode=='backfill':
            time.sleep(1)
            print(f'Filling in missing historical date: {row_date}')
            raw = fetch(url, date=row_date, time_travel='wayback')
        else:
            raw = fetch(url, date=row_date)
        
        if not raw:
            print(f'Could not pull data for {state}: {row_date}')
            continue

        soup = BeautifulSoup(raw, 'html.parser')
        
        positive_case_search = soup.find(text=re.compile('Total positive:|Total positive cases:|Total positive cases \(cumulative\)'))
        if positive_case_search.find_parent('li'):
            cases_str = positive_case_search.find_parent('li').get_text()
        elif positive_case_search.find_parent('p'):
            cases_str = positive_case_search.find_parent('p').get_text()
        elif positive_case_search.find_parent('tr'):
            cases_str = positive_case_search.find_next('td').get_text()
        else:
            raise Exception('Trouble parsing "Total positives"')
        cases_str = cases_str.split('\n')[0]
        cases = int(re.sub(r'[^0-9]', '', cases_str))

        if row_date<'2020-10-14':
            test_html = soup.find(text='Total approximate number of completed tests:')
            test_str = test_html.find_parent('p').get_text()
        else:
            test_html = soup.find(text='Total approximate completed tests (cumulative)')
            test_str = test_html.find_next('td').get_text()
        tested = int(re.sub(r'[^0-9]', '', test_str))

        if row_date<'2020-10-14':
            deaths_html = soup.find('strong', text=re.compile('Total deaths:|Deaths:'))
            deaths_str = deaths_html.find_parent('li').get_text()
        else:
            deaths_html = soup.find('th', text='Total deaths (cumulative)')
            deaths_str = deaths_html.find_next('td').get_text()
        deaths = int(re.sub(r'[^0-9]', '', deaths_str))

        if row_date<'2020-04-10':
            hosp_html = soup.find(text='Total cases requiring hospitalization:')
            hosp_str = hosp_html.find_parent('li').get_text().split('\n')[0]
        else:# row_date<'2020-10-14':
            hosp_patterns = [
                re.compile('Total cases requiring hospitalization:'),
                re.compile('Total cases hospitalized:'),
                'Total cases hospitalized (cumulative)'
            ]
            for pattern in hosp_patterns:
                hosp_search = soup.find(text=pattern)
                if type(hosp_search)!=type(None):
                    break
            if pattern == 'Total cases hospitalized (cumulative)':
                hosp_html = hosp_search.find_next('td').get_text()
            else:
                hosp_html = hosp_search.next
            hosp_str = str(hosp_html)
        #else:
        #    hosp_html = soup.find('th', text='Total deaths (cumulative)')
        #    hosp_str = hosp_html.find_next('td').get_text()

        hosp = int(re.sub(r'[^0-9]', '', hosp_str))



        # Note: "As of 8/20, ethnicity data was incorporated into race categories to more
        # accurately represent our diverse communities and help us better understand how
        # COVID-19 is impacting Black, Hispanic, American Indian, and Asian community members."
        if row_date<'2020-08-20':
            race_df = pd.read_html(str(soup.find(text='Race').find_parent('table')))[0]
            eth_idx = race_df.loc[race_df['Race']=='Ethnicity',:].index[0]

            eth_df = race_df.iloc[eth_idx:,:].copy().reset_index(drop=True)
            eth_df = eth_df.T.set_index(0).T
            eth_df = eth_df.replace({'Unknown/ missing': 'Unknown', 'Unknown/missing': 'Unknown'})

            race_df = race_df.iloc[:eth_idx,:]
            race_df = race_df.replace({'Unknown/ missing': 'Unknown', 'Unknown/missing': 'Unknown'})

            if row_date<'2020-05-13':
                # Percent needs to be converted to number
                race_df['Percent of Cases'] = race_df['Percent of Cases'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                race_df['Percent of Deaths'] = race_df['Percent of Deaths'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                race_df['Number of Cases'] = (race_df['Percent of Cases']*cases).round().astype(int)
                race_df['Number of Deaths'] = (race_df['Percent of Deaths']*deaths).round().astype(int)

                eth_df['Percent of Cases'] = eth_df['Percent of Cases'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                eth_df['Percent of Deaths'] = eth_df['Percent of Deaths'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                eth_df['Number of Cases'] = (eth_df['Percent of Cases']*cases).round().astype(int)
                eth_df['Number of Deaths'] = (eth_df['Percent of Deaths']*deaths).round().astype(int)


            race_df['RaceCol'] = 'Race_Cases [' + race_df['Race'] + ']'
            race_cases_data = race_df.set_index('RaceCol')['Number of Cases'].to_dict()

            race_df['RaceCol'] = 'Race_Deaths [' + race_df['Race'] + ']'
            race_deaths_data = race_df.set_index('RaceCol')['Number of Deaths'].to_dict()
            

            eth_df['EthCol'] = 'Ethnicity_Cases [' + eth_df['Ethnicity'] + ']'
            eth_cases_data = eth_df.set_index('EthCol')['Number of Cases'].to_dict()

            eth_df['EthCol'] = 'Ethnicity_Deaths [' + eth_df['Ethnicity'] + ']'
            eth_deaths_data = eth_df.set_index('EthCol')['Number of Deaths'].to_dict()

        else:
            race_df = pd.read_html(str(soup.find(id='raceethtable')))[0]
            race_df['RaceCol'] = 'RaceEthnicity_Cases [' + race_df['Race/Ethnicity'] + ']'
            race_cases_data = race_df.set_index('RaceCol')['Number of Cases'].to_dict()

            race_df['RaceCol'] = 'RaceEthnicity_Deaths [' + race_df['Race/Ethnicity'] + ']'
            race_deaths_data = race_df.set_index('RaceCol')['Number of Deaths'].to_dict()

            eth_cases_data = {}
            eth_deaths_data = {}


        if row_date<'2020-04-10':
            age_img = soup.find('h4', text='Age').find_next('img')
            age_text = age_img.attrs['alt']
            age_df = pd.read_csv(io.StringIO(age_text), sep=',')
        else:
            age_html = soup.find('th', text='Age Group').find_parent('table')
            age_df = pd.read_html(str(age_html))[0]

        if row_date<'2020-04-12':
            age_df.columns = ['Age', 'Cases']
            age_df = age_df.replace({'Unknown/ missing': 'Unknown', 'Unknown/missing': 'Unknown'})
            age_df['Age'] = age_df['Age'].apply(lambda r: 'Age_Cases [' + ''.join(r.rstrip(' years').split(' ')) + ']')
            age_data = age_df.set_index('Age')['Cases'].to_dict()

        elif row_date<'2020-04-27':
            age_df.columns = ['Age', 'Percent of Cases']
            age_df['Age'] = age_df['Age'].apply(lambda r: ''.join(r.rstrip(' years').split(' ')))
            age_df = age_df.replace({'Unknown/ missing': 'Unknown', 'Unknown/missing': 'Unknown', '<1%': '1%'})
            age_df['Percent of Cases'] = age_df['Percent of Cases'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
            age_df['Cases'] = (age_df['Percent of Cases']*cases).round().astype(int)
            age_df['Columns'] = 'Age_Cases [' + age_df['Age'] + ']'
            age_data = age_df.set_index('Columns')['Cases'].to_dict()

        elif row_date<'2020-05-13':
            age_df.columns = ['Age', 'Percent of Cases', 'Percent of Deaths']
            age_df['Age'] = age_df['Age'].apply(lambda r: ''.join(r.rstrip(' years').split(' ')))
            age_df = age_df.replace({'Unknown/ missing': 'Unknown', 'Unknown/missing': 'Unknown', '<1%': '1%'})
            age_df['Percent of Cases'] = age_df['Percent of Cases'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
            age_df['Cases'] = (age_df['Percent of Cases']*cases).round().astype(int)
            age_df['Columns'] = 'Age_Cases [' + age_df['Age'] + ']'
            age_case_data = age_df.set_index('Columns')['Cases'].to_dict()

            age_df['Percent of Deaths'] = age_df['Percent of Deaths'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
            age_df['Deaths'] = (age_df['Percent of Deaths']*cases).round().astype(int)
            age_df['Columns'] = 'Age_Deaths [' + age_df['Age'] + ']'
            age_death_data = age_df.set_index('Columns')['Deaths'].to_dict()

            age_data = { 
                **age_case_data,
                **age_death_data
            }

        else:
            age_df.columns = ['Age', 'Cases', 'Deaths']
            age_df['Age'] = age_df['Age'].apply(lambda r: ''.join(r.rstrip(' years').split(' ')))
            age_df = age_df.replace({'Unknown/ missing': 'Unknown', 'Unknown/missing': 'Unknown', '<1%': '1%'})

            age_df['Columns'] = 'Age_Cases [' + age_df['Age'] + ']'
            age_case_data = age_df.set_index('Columns')['Cases'].to_dict()

            age_df['Columns'] = 'Age_Deaths [' + age_df['Age'] + ']'
            age_death_data = age_df.set_index('Columns')['Deaths'].to_dict()
        
            age_data = { 
                **age_case_data,
                **age_death_data
            }

        #print(row_date)
        #print(age_data)

        if row_date<'2020-04-10':
            sex_html = soup.find('h4', text='Gender').find_next('ul')
            sex_text = sex_html.get_text()
            sex_list = sex_text.split(',')
            sex_pct = [ int(re.sub(r'[^0-9]', '', s))/100 for s in sex_list ]
            sex_data = {
                'Sex_Cases [Female]': round(cases*sex_pct[0]),
                'Sex_Cases [Male]': round(cases*sex_pct[1]),
                'Sex_Cases [Unknown]': round(cases*(1-sex_pct[0]-sex_pct[1]))
            }

        elif row_date<'2020-05-12':
            sex_html = soup.find('h3', text='Gender').find_next('ul')
            sex_text = sex_html.get_text()
            sex_list = sex_text.split(',')
            sex_pct = [ int(re.sub(r'[^0-9]', '', s))/100 for s in sex_list ]
            sex_data = {
                'Sex_Cases [Female]': round(cases*sex_pct[0]),
                'Sex_Cases [Male]': round(cases*sex_pct[1]),
                'Sex_Cases [Unknown]': round(cases*(1-sex_pct[0]-sex_pct[1]))
            }
        else:
            sex_html = soup.find('h3', text='Gender').find_next('table')
            sex_df = pd.read_html(str(sex_html))[0]
            if row_date=='2020-05-12':
                sex_df['Percent of Cases'] = sex_df['Percent of Cases'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(int)/100
                sex_df['Number of Cases'] = (sex_df['Percent of Cases']*cases).round()
            fc = int(sex_df.loc[sex_df['Gender']=='Female', 'Number of Cases'])
            mc = int(sex_df.loc[sex_df['Gender']=='Male', 'Number of Cases'])
            sex_data = {
                'Sex_Cases [Female]': fc,
                'Sex_Cases [Male]': mc,
                'Sex_Cases [Unknown]': cases-fc-mc
            }

        pullTime = get_pull_time(existing_df, row_date)

        row_data = {
            'state': 'Minnesota',
            'stateAbbrev': 'MN',
            'date': row_date,
            'Cases': cases,
            'Tested': tested,
            'Deaths': deaths,
            'Hospitalizations': hosp,
            **sex_data,
            **age_data,
            **race_cases_data,
            **race_deaths_data,
            **eth_cases_data,
            **eth_deaths_data,
            'pullTime': pullTime
        }
        
        existing_dates = [r['date'] for r in date_rows]
        if row_date in existing_dates:
            idx = existing_dates.index(row_date)
            date_rows[idx] = row_data
        else:
            date_rows.append(row_data)

        timeseries = pd.DataFrame(date_rows)
        #timeseries = timeseries[row_data.keys()]
        timeseries = timeseries.sort_values('date')
        timeseries.to_csv(csv_location, index=False)


if __name__=='__main__':
    run_MN({})
    

