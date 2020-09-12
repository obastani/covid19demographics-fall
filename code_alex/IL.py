from helpers.alex import *

date = datetime.date.today().strftime('%Y-%m-%d')
state = 'IL'

def fetch(url, **kwargs):
    if 'date' not in kwargs.keys() or kwargs['date']==False:
        kwargs['date'] = date
    if 'state' not in kwargs.keys() or kwargs['state']==False:
        kwargs['state'] = state
    return(fetch_(url, **kwargs))

def run_IL(args):
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

        if row_date in ['2020-07-02']:
            print(f'No data provided for {row_date}')
            continue

        url = 'http://www.dph.illinois.gov/sitefiles/COVIDHistoricalTestResults.json'

        if run_mode=='normal':
            raw = fetch(url, date=row_date)
            
        elif run_mode=='backfill':
            time.sleep(1)
            print(f'Filling in missing historical date: {row_date}')

            raw = fetch(url, date=row_date)

            if not raw:
                # Use the cache maintained by https://github.com/covidatlas/li to fill in missing data
                # Cached files can be browsed at: https://s3.console.aws.amazon.com/s3/buckets/listaging-cachebucket-ytmnslhoqzje/?region=us-west-1&tab=overview
                s3_query_url = f'http://listaging-cachebucket-ytmnslhoqzje.s3.amazonaws.com/?prefix=us-il/{row_date}'
                r = requests.get(s3_query_url)
                xml = r.text

                matches = re.findall(r'us\-il/(.*)\.json\.gz', '\n'.join(xml.split('Key')))
                if len(matches)>0:

                    contents_raw = xml.split('</IsTruncated><Contents>')[1].split('</Contents></ListBucketResult>')[0]
                    contents = contents_raw.split('</Contents><Contents>')
                    keys = []
                    for content in contents:
                        lines = content.replace('><', '>\n<').split('\n')
                        for line in lines:
                            if line.startswith('<Key>'):
                                key = line.lstrip('<Key>').rstrip('</Key>')
                            if line.startswith('<LastModified>'):
                                last_modified = line.lstrip('<LastModified>').rstrip('</LastModified>')
                        keys.append({'key': key, 'last_modified': last_modified})

                    sorted_keys = sorted(keys, key=lambda k: k['last_modified'])
                    #print(sorted_keys)
                    newest_key = sorted_keys[-1]['key']

                    import gzip
                    match = matches[-1]
                    cache_url = f'http://listaging-cachebucket-ytmnslhoqzje.s3.amazonaws.com/{newest_key}'
                    print('Fetching COVIDAtlas cached:\n'+cache_url)

                    json_gz = requests.get(cache_url)

                    gzip_file = io.BytesIO(json_gz.content)
                    with gzip.open(gzip_file, 'rt') as f:
                        raw = f.read()
                    
                    # Save fetched content to local cache
                    filename = cache_filename(url, date=row_date, state='IL')
                    folderpath = Path(project_root, state, 'raw')
                    filepath = Path(folderpath, filename)
                    print('Saving cached data to: '+ filename)
                    with open(filepath, 'w+') as file:
                        file.write(raw)
                

        if not raw:
            print(f'Could not pull data for {state}: {row_date}')
            continue

        raw_json = json.loads(raw)

        # IL messed up on their data formatting for 7/31; however
        # data for 7/31 can be read from file for 8/1
        if row_date=='2020-07-31':
            raw2 = fetch(url, date='2020-08-01')
            totals_json = json.loads(raw2)
        else:
            totals_json = raw_json

        DF = pd.DataFrame(totals_json['state_testing_results']['values'])
        #print(DF.tail())
        DF = DF.rename(columns = {
            'confirmed_cases':'Cases',
            'deaths': 'Deaths',
            'testDate': 'date', 
            'total_tested': 'Tested'
        })
        DF['date'] = DF['date'].astype(str).apply(lambda r: dparser.parse(r).strftime('%Y-%m-%d'))
        totals = DF.loc[DF.date==row_date,:].iloc[0,:].to_dict()

        age_df = pd.DataFrame(raw_json['demographics']['age'])
        age_df = age_df.replace({'<20':'0-20'})
        age_df['AgeCol'] = 'Age_Cases [' + age_df['age_group'] + ']'
        age_cases_data = age_df.set_index('AgeCol')['count'].to_dict()
        age_df['AgeCol'] = 'Age_Deaths [' + age_df['age_group'] + ']'
        age_deaths_data = age_df.set_index('AgeCol')['deaths'].to_dict()


        race_df = pd.DataFrame(raw_json['demographics']['race'])
        race_df['RaceCol'] = 'Race_Cases [' + race_df['description'] + ']'
        race_cases_data = race_df.set_index('RaceCol')['count'].to_dict()
        race_df['RaceCol'] = 'Race_Deaths [' + race_df['description'] + ']'
        race_deaths_data = race_df.set_index('RaceCol')['deaths'].to_dict()


        sex_df = pd.DataFrame(raw_json['demographics']['gender'])
        sex_df['SexCol'] = 'Sex_Cases [' + sex_df['description'] + ']'
        sex_cases_data = sex_df.set_index('SexCol')['count'].to_dict()
        sex_df['SexCol'] = 'Sex_Deaths [' + sex_df['description'] + ']'
        sex_deaths_data = sex_df.set_index('SexCol')['deaths'].to_dict()


        pullTime = get_pull_time(existing_df, row_date)

        row_data = {
            'state': 'Illinois',
            'stateAbbrev': 'IL',
            **totals,
            **sex_cases_data,
            **sex_deaths_data,
            **age_cases_data,
            **age_deaths_data,
            **race_cases_data,
            **race_deaths_data,
            'pullTime': pullTime
        }

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
    run_IL({})
    

