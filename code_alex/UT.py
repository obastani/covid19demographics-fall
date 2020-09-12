from helpers.alex import *

date = datetime.date.today().strftime('%Y-%m-%d')
state = 'UT'

def fetch(url, **kwargs):
    if 'date' not in kwargs.keys() or kwargs['date']==False:
        kwargs['date'] = date
    if 'state' not in kwargs.keys() or kwargs['state']==False:
        kwargs['state'] = state
    return(fetch_(url, **kwargs))

def run_UT(args):
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


    
    earliest_date_w_demographics = '2020-04-02'

    # Whether to fetch current date, re-do all from raw data, or backfill with Wayback
    run_mode =  'normal' # normal, from scratch, backfill

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
        url = 'https://coronavirus-dashboard.utah.gov/'

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
        
        # Top level data
        cases_html = soup.find('div', id=re.compile('covid\-19\-cases'))
        cases_str = cases_html.find('span', {'class':'value-output'}).get_text()
        cases = int(re.sub(r'[^0-9]', '', cases_str))


        # Starting around July 17 Utah started reporting separate numbers for
        # "people tested" and "total tests reported" (since one person can be
        # tested more than once). Prior to that, they appear to have only
        # repoted the "people tested" number.
        patterns = [
            re.compile('total\-reported\-people\-tested'),
            re.compile('reported\-people\-tested'),
            re.compile('total\-people\-tested')
        ]
        for p in patterns:
            tested_html = soup.find('div', id=p)
            if type(tested_html)!=type(None):
                break

        tested_str = tested_html.find('span', {'class':'value-output'}).get_text()
        tested = int(re.sub(r'[^0-9]', '', tested_str))

        tests = False
        try:
            tests_html = soup.find('div', id=re.compile('total\-tests\-reported'))
            tests_str = tests_html.find('span', {'class':'value-output'}).get_text()
            tests = int(re.sub(r'[^0-9]', '', tests_str))
        except:
            pass


        # hospitalizations aggregated from age breakdown data belwo
        #hosp_html = soup.find('div', id=re.compile('covid\-19\-hospitalizations'))
        #hosp_str = hosp_html.find('span', {'class':'value-output'}).get_text()
        #hosp = int(re.sub(r'[^0-9]', '', hosp_str))
        
        deaths_html = soup.find('div', id=re.compile('covid\-19\-deaths'))
        deaths_str = deaths_html.find('span', {'class':'value-output'}).get_text()
        deaths = int(re.sub(r'[^0-9]', '', deaths_str))


        # Overall age breakdown
        patterns = [
            re.compile('utah\-residents\-with\-covid\-19\-demographics\-table'),
            re.compile('total\-utah\-residents\-with\-covid\-19\-by\-age'),
            re.compile('total\-people\-living\-in\-utah\-with\-covid\-19\-by\-age')
        ]
        for p in patterns:
            age_html = soup.find('div', id=p)
            if type(age_html)!=type(None):
                break
        
        age_json = json.loads(age_html.find('script').text)
        age_df = pd.DataFrame(age_json['x']['data']).T
        age_df.columns = pd.read_html(age_json['x']['container'])[0].columns
        age_df['Age Group'] = age_df['Age Group'].apply(lambda r: r.rstrip(' years'))
        age_df.loc[0, 'Age Group'] = '0-1'
        age_df['Age Group'] = 'Age [' + age_df['Age Group'] + ']'
        age_df = age_df.set_index('Age Group')
        age_data = age_df['Case Count'].astype(int).to_dict()


        # Age breakdown by sex
        patterns = [
            re.compile('utah\-residents\-with\-covid\-19\-demographics\-chart'),
            re.compile('total\-people\-living\-in\-utah\-with\-covid-19\-by\-age\-chart'),
            re.compile('total\-utah\-residents\-with\-covid\-19\-by\-age\-chart')
        ]
        for p in patterns:
            age_sex_html = soup.find('div', id=p)
            if type(age_sex_html)!=type(None):
                break

        age_sex_json = json.loads(age_sex_html.find('script').text)

        female_age_json = [d for d in age_sex_json['x']['data'] if d['name']=='Female'][0]
        female_text = pd.Series(female_age_json['text'])
        female_counts = pd.DataFrame(female_text.apply(lambda r: re.findall(f'Count: ([0-9]+)', r)[0]))
        female_age_bins = female_text.apply(lambda r: re.findall(f'Age Group: ([0-9][0-9]?\-[0-9][0-9]?|[0-9][0-9]\+|Unknown)', r)[0])
        #female_age_bins = female_age_bins.replace({'0-1':'<1'})
        female_counts['Age Group'] = female_age_bins
        female_counts['Age Group'] = 'Female_Age [' + female_counts['Age Group'] + ']'
        female_counts = female_counts.set_index('Age Group')[0].astype(int)
        all_female = female_counts.sum()
        female_age_data = female_counts.to_dict()

        male_age_json = [d for d in age_sex_json['x']['data'] if d['name']=='Male'][0]
        male_text = pd.Series(male_age_json['text'])
        male_counts = pd.DataFrame(male_text.apply(lambda r: re.findall(f'Count: ([0-9]+)', r)[0]))
        male_age_bins = male_text.apply(lambda r: re.findall(f'Age Group: ([0-9][0-9]?\-[0-9][0-9]?|[0-9][0-9]\+|Unknown)', r)[0])
        #male_age_bins = male_age_bins.replace({'0-1':'<1'})
        male_counts['Age Group'] = male_age_bins
        male_counts['Age Group'] = 'Male_Age [' + male_counts['Age Group'] + ']'
        male_counts = male_counts.set_index('Age Group')[0].astype(int)
        all_male = male_counts.sum()
        male_age_data = male_counts.to_dict()

        sex_data = {
            'Female': all_female,
            'Male': all_male,
            **female_age_data,
            **male_age_data
        }



        # Hospitalization data
        hosp_pattern = 'utah\-residents\-who\-have\-been\-hospitalized\-with\-covid\-19\-by\-age|total\-utah\-covid\-19\-cases\-by\-hospitalization\-status\-and\-age'
        hosp_age_html = soup.find('div', id=re.compile(hosp_pattern))
        hosp_age_json = json.loads(hosp_age_html.find('script').text)

        hosp_bins = pd.Series(hosp_age_json['x']['layout']['xaxis']['ticktext'])
        #hosp_bins = hosp_bins.replace({'0-1':'<1'})

        hosp_index = 'Hospitalized_Age [' + hosp_bins + ']'
        hosp_by_age_df = pd.DataFrame([], index=hosp_index)
        hosp_by_age_df[0] = 0
        hosp_by_age = [d for d in  hosp_age_json['x']['data'] if d['name']=='Yes'][0]
        hosp_by_age_df.loc[hosp_by_age_df.index[np.array(hosp_by_age['x'])-1],0] = hosp_by_age['y']
        hosp_by_age_data = hosp_by_age_df[0].to_dict()

        hosp_index = 'HospitalizedPending_Age [' + hosp_bins + ']'
        hosp_pending_by_age_df = pd.DataFrame([], index=hosp_index)
        hosp_pending_by_age_df[0] = 0
        hosp_pending_by_age = [d for d in  hosp_age_json['x']['data'] if d['name']=='Under Investigation'][0]
        hosp_pending_by_age_df.loc[hosp_pending_by_age_df.index[np.array(hosp_pending_by_age['x'])-1],0] = hosp_pending_by_age['y']
        hosp_pending_by_age_data = hosp_pending_by_age_df[0].to_dict()

        hosp_total = hosp_by_age_df[0].sum()
        hosp_pending_total = hosp_pending_by_age_df[0].sum()


        hosp_data = {
            'Hospitalizations': hosp_total,
            **hosp_by_age_data,
            'HospitalizationsPending': hosp_pending_total,
            **hosp_pending_by_age_data
        }

        if row_date>'2020-04-15':
            race_html = soup.find('div', id=re.compile('by\-raceethnicity'))
            race_json = json.loads(race_html.find('script').text)
            race_df = pd.DataFrame(race_json['x']['data']).T
            race_df.columns = pd.read_html(race_json['x']['container'])[0].columns
            race_df = race_df.replace({'&lt;5':'<5'})
            race_df = race_df.rename(columns={'Cases': 'Case Count'})

            race_df['Columns'] = 'Race_Cases [' + race_df['Race/Ethnicity'] + ']'
            race_cases = race_df.set_index('Columns')['Case Count'].astype(int).to_dict()

            race_df['Columns'] = 'Race_Hospitalizations [' + race_df['Race/Ethnicity'] + ']'
            race_hosp = race_df.set_index('Columns')['Hospitalizations'].to_dict()

            if row_date>'2020-06-14':
                race_df['Columns'] = 'Race_Deaths [' + race_df['Race/Ethnicity'] + ']'
                race_deaths = race_df.set_index('Columns')['Deaths'].to_dict()
            else:
                race_deaths = {}

            race_data = {
                **race_cases,
                **race_hosp,
                **race_deaths
            }

        else:
            race_data = {}


        pullTime = get_pull_time(existing_df, row_date)

        row_data = {
            'state': 'Utah',
            'stateAbbrev': 'UT',
            'date': row_date,
            'Cases': cases,
            'Tested': tested,
            'Deaths': deaths,
            **hosp_data,
            **age_data,
            **sex_data,
            **race_data,
            'pullTime': pullTime
        }

        if tests:
            row_data['Tests'] = tests
        
        existing_dates = [r['date'] for r in date_rows]
        if row_date in existing_dates:
            idx = existing_dates.index(row_date)
            date_rows[idx] = row_data
        else:
            date_rows.append(row_data)

    timeseries = pd.DataFrame(date_rows)
    timeseries = timeseries.sort_values('date')
    timeseries.to_csv(csv_location, index=False)


if __name__=='__main__':
    run_UT({})
