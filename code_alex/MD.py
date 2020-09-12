from helpers.alex import *

date = datetime.date.today().strftime('%Y-%m-%d')
state = 'MD'

def fetch(url, **kwargs):
    if 'date' not in kwargs.keys() or kwargs['date']==False:
        kwargs['date'] = date
    if 'state' not in kwargs.keys() or kwargs['state']==False:
        kwargs['state'] = state
    return(fetch_(url, **kwargs))

def run_MD(args):
    # Load existing data
    data_folder = Path(project_root, state, 'data')
    csv_location = Path(data_folder, 'data.csv')
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    if Path(data_folder, 'data.csv').exists():
        existing_df = pd.read_csv(csv_location)
    else:
        existing_df = pd.DataFrame([])
    
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

    earliest_date_w_demographics = '2020-03-28'

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
        # Web archive has data from 3/27, but the breakdown is limited
        # e.g., 0-18, 18-64, 65+
        #if row_date == '2020-03-27':
        #    url = 'https://web.archive.org/web/20200326220245id_/https://coronavirus.maryland.gov/'
        #    raw = fetch(url, date=row_date, time_travel=True)

        url = 'https://coronavirus.maryland.gov/'

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
        import urllib.parse
        site_injection_raw = soup.find(attrs={'id':'site-injection'}).get_text().strip().split('window.__SITE=')[1]
        site_injection_str = urllib.parse.unquote(site_injection_raw)
        if row_date>'2020-05-14':
            site_injection_str = site_injection_str[1:-1]
        site_injection_data = json.loads(site_injection_str)
        sections = site_injection_data['site']['data']['values']['layout']['sections']
        components = [s for s in sections if 'by age range' in json.dumps(s).lower()][0]['rows'][0]['cards']

        # Get total counts
        soup = BeautifulSoup(components[1]['component']['settings']['markdown'], 'html.parser')
        
        totals_tag = soup.find('p', {'class':'topBoxH1Text'})
        if not totals_tag:
            totals_tag = soup.find('p', {'class':'topBlackBoxHeader'})
        totals = totals_tag.get_text().strip().split('\n')

        #print(totals)

        current_hosp = False
        deaths = 0
        for row in totals:
            if ':' not in row:
                continue
            name, val = row.split(':')
            name = name.lower()
            val = int(re.sub(r'[^0-9]', '', val))
            if 'confirmed cases' in name:
                total_cases = val
            
            elif 'negative' in name:
                neg = val
            
            elif 'deaths' in name:
                # Starting 4/15, includes "probable" deaths 
                # as well as confirmed deaths
                deaths += val
            
            elif name.startswith('hosp') or name.startswith('ever hosp'):
                hosp = val

            elif name.startswith('currently hosp'):
                current_hosp = val
                

        # Get age and gender breakdown
        tables = pd.read_html(components[1]['component']['settings']['markdown'])
        #Deaths columns added 2020-04-09
        if row_date<'2020-04-09':
            age_df = tables[1].copy()
            gender_data = age_df.tail(1)
            age_df = age_df.iloc[:-1,:]

            age_df.columns = ['Age', 'Cases']
            age_df['Colnames'] = 'Age_Cases ['+ age_df['Age'] +']'
            
            age_df['Cases'] = age_df['Cases'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(int)
            age_case_data = age_df[['Colnames','Cases']].set_index('Colnames')['Cases'].to_dict()
            age_death_data = {}

            gender_str = gender_data.iloc[0,0]
            female_match = re.findall(f'Female:(.*)Male', gender_str)
            female_str = female_match[0]
            female_count = int(re.sub(r'[^0-9]', '', female_str))
            male_match = re.findall(f'Male:(.*)', gender_str)
            male_str = male_match[0]
            male_count = int(re.sub(r'[^0-9]', '', male_str))

            sex_data = {
                'Sex_Cases [Female]': female_count,
                'Sex_Cases [Male]': male_count
            }

            race_data = {}

        else:
            age_df = tables[1].copy()
            if age_df.shape[1]==3:
                age_df.columns = ['Age', 'Cases', 'Deaths']
            else:
                age_df.columns = ['Age', 'Cases', 'Deaths', 'ProbDeaths']
                age_df['ProbDeaths'] = age_df['ProbDeaths'].astype(str).apply(lambda r: re.sub(r'[^0-9]', '', r)).replace({'':'0'}).astype(int)    

            if 'age' in str(age_df.iloc[0,0]).lower():
                age_df = age_df.iloc[1:,:]

            age_df = age_df.replace('Data Not Available','Unknown')

            age_df['Cases'] = age_df['Cases'].astype(str).apply(lambda r: re.sub(r'[^0-9]', '', r)).replace({'':'0'}).astype(int)

            age_df['Deaths'] = age_df['Deaths'].astype(str).apply(lambda r: re.sub(r'[^0-9]', '', r)).replace({'':'0'}).astype(int)
            if 'ProbDeaths' in age_df.columns:
                age_df['Deaths'] = age_df['Deaths'] + age_df['ProbDeaths']

            gender_df = age_df.tail(2)

            age_df = age_df.iloc[:-2,:]
            age_df['Colnames'] = 'Age_Deaths ['+ age_df['Age'] +']'
            age_death_data = age_df[['Colnames','Deaths']].set_index('Colnames')['Deaths'].to_dict()
            
            age_df['Colnames'] = 'Age_Cases ['+ age_df['Age'] +']'            
            age_case_data = age_df[['Colnames','Cases']].set_index('Colnames')['Cases'].to_dict()

            sex_data = {
                'Sex_Cases [Female]': gender_df.iloc[0,1],
                'Sex_Cases [Male]': gender_df.iloc[1,1],
                'Sex_Deaths [Female]': gender_df.iloc[0,2],
                'Sex_Deaths [Male]': gender_df.iloc[1,2],
            }

            race_df = tables[2].copy()
            race_df = race_df.dropna('rows')

            if race_df.shape[1]==3:
                race_df.columns = ['Race', 'Cases', 'Deaths']
            else:
                race_df.columns = ['Race', 'Cases', 'Deaths', 'ProbDeaths']
                race_df['ProbDeaths'] = race_df['ProbDeaths'].astype(str).apply(lambda r: re.sub(r'[^0-9]', '', r)).replace({'':'0'}).astype(int)  

            if 'race' in str(race_df.iloc[0,0]).lower():
                race_df = race_df.iloc[1:,:]

            race_df = race_df.replace('Data not available','Unknown').replace('Data Not Available','Unknown')

            # Maryland changed how they report Hispanic ethnicity
            # starting 4/15. Presumably, anyone of Hispanic ethnicity
            # (regardless of race) is now reported as "Hispanic".
            # All other classes are reported as "Race (NH)", for "non-Hispanic".
            # Prior to this point, I assume Hispanic cases were counted in
            # with whicheve race they identified with.
            race_df['Race'] = race_df['Race'].str.rstrip(' (NH)')

            race_df['Cases'] = race_df['Cases'].astype(str).apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(int)
            race_df['Deaths'] = race_df['Deaths'].astype(str).apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(int)
            
            if 'ProbDeaths' in race_df.columns:
                race_df['Deaths'] = race_df['Deaths'] + race_df['ProbDeaths']

            race_df['Colnames'] = 'Race_Deaths ['+ race_df['Race'] +']'
            race_death_data = race_df[['Colnames','Deaths']].set_index('Colnames')['Deaths'].to_dict()
            
            race_df['Colnames'] = 'Race_Cases ['+ race_df['Race'] +']'
            race_case_data = race_df[['Colnames','Cases']].set_index('Colnames')['Cases'].to_dict()

            race_data = {
                **race_case_data,
                **race_death_data
            }

        
        pullTime = get_pull_time(existing_df, row_date)

        row_data = {
            'state': 'Maryland',
            'stateAbbrev': 'MD',
            'date': row_date,
            'Cases': total_cases,
            'Tested': total_cases + neg,
            'Hospitalizations': hosp,
            'Deaths': deaths,
            **age_case_data,
            **age_death_data,
            **sex_data,
            **race_data,
            'pullTime': pullTime
        }

        if current_hosp:
            row_data["ActiveHospitalizations"] = current_hosp

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
    run_MD({})
    

