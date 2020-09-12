from helpers.alex import *
from urllib.request import urlopen, Request
import csv

date = datetime.date.today().strftime('%Y-%m-%d')
state = 'MI'

def fetch(url, **kwargs):
    if 'date' not in kwargs.keys() or kwargs['date']==False:
        kwargs['date'] = date
    if 'state' not in kwargs.keys() or kwargs['state']==False:
        kwargs['state'] = state
    return(fetch_(url, **kwargs))

def get_historical():
    # Getting days we missed in July for cases by demographics - Andrew
    start_date = datetime.datetime(2020,6,29)
    end_date = datetime.datetime(2020,8,3)
    dates = []
    while start_date != end_date:
        dates.append(start_date)
        start_date = start_date + datetime.timedelta(days=1)

    raw_name = '../MI/raw'
    out = []

    for dt_date in dates:
        date = dt_date.strftime("%Y%m%d")
        url = ("https://web.archive.org/web/%s/https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html" % date)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = Request(url=url, headers=headers) 
        html = urlopen(req).read() 
        soup = BeautifulSoup(html, "html.parser")
        link = (soup.find('a', text='Cases by Demographics Statewide'))['href'].split('https://')
        csv_link = 'https://' + link[1]
        exp_headers = ['case_status', 'agecat', 'racecat', 'sex', 'cases', 'deaths']
        df = pd.read_excel(csv_link)
        df.columns = df.columns.str.lower()
        df.to_csv(raw_name + "/" + str(dt_date) + '.csv')
        if len(exp_headers) != len(df.columns):
            print("Unexpected number of columns")
            continue
        for head in df.columns:
            if head not in exp_headers:
                raise Exception('Unexpected header')
        rows = df.to_dict(orient='records')
        for row in rows:
            row["Date"] = str(dt_date)
        out.extend(rows)
    
    data = '../MI/data/data_dem_jul.csv'
    for row in out:
        fields = sorted([x for x in row])
        exists = os.path.exists(data)
        with open(data, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([row[x] for x in fields])


def run_MI(args):
    # get_historical()
    # exit()
    # Load existing data
    data_folder = Path(project_root, state, 'data')
    csv_location = Path(data_folder, 'data.csv')
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    if Path(data_folder, 'data.csv').exists():
        existing_df = pd.read_csv(csv_location)
    else:
        existing_df = pd.DataFrame([])
    


    ## Fetch raw data
    
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

    earliest_date_w_demographics = '2020-03-21'

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
        row_date_obj = dparser.parse(row_date).date()

        if row_date<'2020-06-05':
            # Fetch historical data from https://github.com/lazd/coronadatascraper-cache
            if row_date<'2020-03-30':
                url = 'https://www.michigan.gov/coronavirus/0,9753,7-406-98163-520743--,00.html'
                m = hashlib.md5()
                m.update(url.encode('utf-8'))
                url_hash = m.hexdigest()
                cds_date = f'{row_date_obj.year}-{row_date_obj.month}-{row_date_obj.day}'
                cds_cache_url = f'https://github.com/lazd/coronadatascraper-cache/raw/master/{cds_date}/{url_hash}.html'
                raw = fetch(cds_cache_url, date=row_date, time_travel=True)
            elif row_date<'2020-04-02':
                # Fall back to our own scraped data
                url = 'https://www.michigan.gov/coronavirus/0,9753,7-406-98163-520743--,00.html'
                raw = fetch(url, date=row_date)
            elif row_date<'2020-06-03':
                # URL changed April 2nd
                url = 'https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html'
                raw = fetch(url, date=row_date)
            else:
                url = 'https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html'
                raw = fetch(url, date=row_date)

            # Michigan started posting time-series testing data on 4/8
            # Will download to our data every 7 days
            if row_date>='2020-04-08' and\
                (datetime.date(2020,4,8) - row_date_obj).days % 7 == 0:
                
                url = 'https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173_99225---,00.html'
                _ = fetch(url, date=row_date)

            # MI provides tons of data about hospital supplies/capacity
            # broken down by region; saving in case useful in future
            if row_date>='2020-04-21':
                url = 'https://www.michigan.gov/coronavirus/0,9753,7-406-98159-523641--,00.html'
                _ = fetch(url, date=row_date)
                
            if not raw:
                print(f'Could not pull data for {state}: {row_date}')
                continue

            soup = BeautifulSoup(raw, 'html.parser')
            county_table = soup.find(string=re.compile(r'Cases by County|Confirmed COVID-19 Cases by Jurisdiction')).find_parent('table')

            # Total counts
            county_df = pd.read_html(str(county_table))[0]
            if county_df.columns[0]!='County':
                #county_df = county_df.T.set_index(0).T
                county_df.columns = ['County', 'Confirmed Cases', 'Reported Deaths']

            if row_date<'2020-04-16':
                total_cases = int(county_df.tail(1)['Cases'])
            elif row_date=='2020-04-20':
                total_cases = int(county_df.iloc[-1,1])
            else:
                total_cases = int(county_df.tail(1)['Confirmed Cases'])
                
            if row_date<'2020-04-03':
                deaths = int(county_df.tail(1)['Deaths'])
            elif row_date=='2020-04-20':
                deaths = int(county_df.iloc[-1,2])
            else:
                if 'Reported Death' in county_df.columns:
                    deaths = int(county_df.tail(1)['Reported Death'])
                else:
                    deaths = int(county_df.tail(1)['Reported Deaths'])

            # Counts by sex
            sex_table = soup.find(string=re.compile(r'Cases by Sex')).find_parent('table')
            sex_df_all = pd.read_html(str(sex_table))[0]

            sex_df_all = sex_df_all.replace({'Unknown': 'SexUnknown'})

            if row_date<'2020-04-02':
                sex_df = sex_df_all.set_index('Sex')['%']
            else:
                sex_df = sex_df_all.set_index('Sex')['Percentage of Overall Cases by Sex']
                
            sex_df = sex_df.apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
            sex_df = (sex_df*total_cases).astype(int)
            sex_data = sex_df.to_dict()

            # Deceased counts by sex
            sex_deceased_match = soup.find(string=re.compile(r'Deceased by Sex'))
            if sex_deceased_match:
                if row_date<'2020-04-02':
                    sex_deceased_table = sex_deceased_match.find_parent('table')
                    sex_deceased_df = pd.read_html(str(sex_deceased_table))[0]
                    sex_deceased_df['Sex'] = sex_deceased_df['Sex'] + '_Deceased'
                    sex_deceased_df = sex_deceased_df.set_index('Sex')['%']
                else:
                    sex_deceased_df = sex_df_all[['Sex','Percentage of Deceased Cases by Sex']].copy()
                    sex_deceased_df['Sex'] = sex_deceased_df['Sex'] + '_Deceased'
                    sex_deceased_df = sex_deceased_df.set_index('Sex')['Percentage of Deceased Cases by Sex']

                sex_deceased_df = sex_deceased_df.apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                sex_deceased_df = (sex_deceased_df*deaths).astype(int)
                sex_deceased_data = sex_deceased_df.to_dict()
            else:
                sex_deceased_data = {}

            # Counts by age
            age_table = soup.find(string=re.compile(r'Cases by Age')).find_parent('table')
            age_df_all = pd.read_html(str(age_table))[0]


            if row_date < '2020-04-02':
                age_df = age_df_all.drop(0).copy()
                age_df.columns = ['Age', 'Percent']
            else:
                age_df = age_df_all[['Age', 'Percentage of Overall Cases by Age']].copy()
                age_df.columns = ['Age','Percent']

            age_df['Percent'] = age_df['Percent'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
            age_df['Age'] = age_df['Age'].apply(lambda r: re.sub(r' to ', '-', r)).apply(lambda r: re.sub(r' years', '', r))
            age_df['Age'] = 'Age ['+ age_df['Age'] +']'
            age_df['Counts'] = (age_df['Percent']*total_cases).astype(int)
            age_data = age_df[['Age','Counts']].set_index('Age')['Counts'].to_dict()

            if row_date>='2020-04-02':
                age_deceased_df = age_df_all[['Age', 'Percentage of Deceased Cases by Age']].copy()
                age_deceased_df.columns = ['Age','Percent']
                age_deceased_df['Percent'] = age_deceased_df['Percent'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                age_deceased_df['Age'] = age_deceased_df['Age'].apply(lambda r: re.sub(r' to ', '-', r)).apply(lambda r: re.sub(r' years', '', r))
                age_deceased_df['Age'] = 'Age ['+ age_deceased_df['Age'] +']'
                age_deceased_df['Counts'] = (age_deceased_df['Percent']*deaths).astype(int)
                age_deceased_data = age_deceased_df[['Age','Counts']].set_index('Age')['Counts'].to_dict()
                
            else:
                age_deceased_data = {}
                

            # Race & ethnicity data
            if row_date>='2020-04-02':
                race_table = soup.find(string=re.compile(r'Cases by Race')).find_parent('table')
                race_df_all = pd.read_html(str(race_table))[0]
                race_df_all.columns = ['Race', 'Cases', 'Deceased']
                
                race_cases = race_df_all[['Race','Cases']].copy()
                race_cases['Race'] = 'Race [' + race_cases['Race'] + ']'
                race_cases = race_cases.set_index('Race')
                race_cases['Cases'] = race_cases['Cases'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                race_cases['Cases'] = (race_cases['Cases']*total_cases).round()
                race_data = race_cases['Cases'].to_dict()
                
                race_deceased = race_df_all[['Race','Deceased']].copy()
                race_deceased['Race'] = 'Race_Deceased [' + race_deceased['Race'] + ']'
                race_deceased = race_deceased.set_index('Race')
                race_deceased['Deceased'] = race_deceased['Deceased'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                race_deceased['Deceased'] = (race_deceased['Deceased']*deaths).round()
                race_deceased_data = race_deceased['Deceased'].to_dict()
                
                
                
                eth_table = soup.find(string=re.compile(r'Cases by Ethnicity')).find_parent('table')
                eth_df_all = pd.read_html(str(eth_table))[0]
                eth_df_all.columns = ['Ethnicity', 'Cases', 'Deceased']
                
                eth_cases = eth_df_all[['Ethnicity','Cases']].copy()
                eth_cases['Ethnicity'] = 'Ethnicity [' + eth_cases['Ethnicity'] + ']'
                eth_cases = eth_cases.set_index('Ethnicity')
                eth_cases['Cases'] = eth_cases['Cases'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                eth_cases['Cases'] = (eth_cases['Cases']*total_cases).round()
                ethnicity_data = eth_cases['Cases'].to_dict()
                
                eth_deceased = eth_df_all[['Ethnicity','Deceased']].copy()
                eth_deceased['Ethnicity'] = 'Ethnicity_Deceased [' + eth_deceased['Ethnicity'] + ']'
                eth_deceased = eth_deceased.set_index('Ethnicity')
                eth_deceased['Deceased'] = eth_deceased['Deceased'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
                eth_deceased['Deceased'] = (eth_deceased['Deceased']*deaths).round()
                ethnicity_deceased_data = eth_deceased['Deceased'].to_dict()
                
                # State started posting time series for test data; see above
                #tests_table = soup.find(string=re.compile(r'Cumulative Number of Specimens Tested')).find_parent('table')
                #tests_df = pd.read_html(str(tests_table))[0]
                #total_tests = int(tests_df.loc[tests_df['Lab Type']=='Grand Total', 'Total Specimens Tested'])


            else:
                #total_tests = np.nan
                race_data = {}
                race_deceased_data = {}
                ethnicity_data = {}
                ethnicity_deceased_data = {}

        else:
            # Data changed to PowerBI and Excel sheets on June 5.

            #print(row_date)

            url = 'https://www.michigan.gov/documents/coronavirus/Cases_and_Deaths_by_County_693160_7.xlsx'
            raw_xlsx = fetch(url, extension='xlsx', date=row_date)
            cases_df = pd.read_excel(raw_xlsx, engine='xlrd')
            total_cases = cases_df['Cases'].sum()
            deaths = cases_df['Deaths'].sum()


            url = 'https://www.michigan.gov/documents/coronavirus/Cases_by_Demographics_Statewide_693162_7.xlsx'
            raw_xlsx = fetch(url, extension='xlsx', date=row_date)
            demo_df = pd.read_excel(raw_xlsx, engine='xlrd')
            demo_df['Cases'] = demo_df['Cases'].replace({'Suppressed': 1}).astype(int)
            demo_df['Deaths'] = demo_df['Deaths'].replace({'Suppressed': 1}).astype(int)


            age_df = demo_df.groupby('AgeCat')[['Cases', 'Deaths']].sum()
            age_df['Colnames'] = 'Age_Cases [' + age_df.index + ']'
            age_data = age_df.set_index('Colnames')['Cases'].to_dict()
            age_df['Colnames'] = 'Age_Deaths [' + age_df.index + ']'
            age_deceased_data = age_df.set_index('Colnames')['Deaths'].to_dict()

            sex_df = demo_df.groupby('SEX')[['Cases', 'Deaths']].sum()
            sex_df['Colnames'] = 'Sex_Cases [' + sex_df.index + ']'
            sex_data = sex_df.set_index('Colnames')['Cases'].to_dict()
            sex_df['Colnames'] = 'Sex_Deaths [' + sex_df.index + ']'
            sex_deceased_data = sex_df.set_index('Colnames')['Deaths'].to_dict()

            race_df = demo_df.groupby('RaceCat')[['Cases', 'Deaths']].sum()
            race_df['Colnames'] = 'Race_Cases [' + race_df.index + ']'
            race_data = race_df.set_index('Colnames')['Cases'].to_dict()
            race_df['Colnames'] = 'Race_Deaths [' + race_df.index + ']'
            race_deceased_data = race_df.set_index('Colnames')['Deaths'].to_dict()

            # Ethnicity data still in HTML 
            url = 'https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html'
            raw = fetch(url, date=row_date)
            soup = BeautifulSoup(raw, 'html.parser')

            eth_table = soup.find(string=re.compile(r'Cases by Hispanic/Latino Ethnicity')).find_parent('table')
            eth_df_all = pd.read_html(str(eth_table))[0]
            eth_df_all.columns = ['Ethnicity', 'Cases', 'Deceased']
            
            eth_cases = eth_df_all[['Ethnicity','Cases']].copy()
            eth_cases['Ethnicity'] = 'Ethnicity_Cases [' + eth_cases['Ethnicity'] + ']'
            eth_cases = eth_cases.set_index('Ethnicity')
            eth_cases['Cases'] = eth_cases['Cases'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
            eth_cases['Cases'] = (eth_cases['Cases']*total_cases).round()
            ethnicity_data = eth_cases['Cases'].to_dict()
            
            eth_deceased = eth_df_all[['Ethnicity','Deceased']].copy()
            eth_deceased['Ethnicity'] = 'Ethnicity_Deaths [' + eth_deceased['Ethnicity'] + ']'
            eth_deceased = eth_deceased.set_index('Ethnicity')
            eth_deceased['Deceased'] = eth_deceased['Deceased'].apply(lambda r: re.sub(r'[^0-9]', '', r)).astype(float)/100
            eth_deceased['Deceased'] = (eth_deceased['Deceased']*deaths).round()
            ethnicity_deceased_data = eth_deceased['Deceased'].to_dict()


        pullTime = get_pull_time(existing_df, row_date)

        row_data = {
            'state': 'Michigan',
            'stateAbbrev': 'MI',
            'date': row_date,
            'Cases': total_cases,
            'Deaths': deaths,
            **age_data,
            **age_deceased_data,
            **sex_data,
            **sex_deceased_data,
            **race_data,
            **race_deceased_data,
            **ethnicity_data,
            **ethnicity_deceased_data,
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
    timeseries.to_csv(csv_location, index=False)

if __name__=='__main__':
    run_MI({})
    

