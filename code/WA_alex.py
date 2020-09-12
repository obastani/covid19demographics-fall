from helpers.alex import *
import hashlib

date = datetime.date.today().strftime('%Y-%m-%d')
state = 'WA'

def fetch(url, **kwargs):
    if 'date' not in kwargs.keys() or kwargs['date']==False:
        kwargs['date'] = date
    if 'state' not in kwargs.keys() or kwargs['state']==False:
        kwargs['state'] = state
    return(fetch_(url, **kwargs))


def run_WA(args):
    # Fetch raw data for date in args
    if 'day' in args:
        date = datetime.date(args['year'], args['month'], args['day']).strftime('%Y-%m-%d')
    else:
        date = datetime.date.today().strftime('%Y-%m-%d')

    
    
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
            date_obj = datetime.date.today() #- datetime.timedelta(days=1)
        date = date_obj.strftime('%Y-%m-%d')

    earliest_date_w_demographics = '2020-03-21'
    date_list = pd.date_range(start=earliest_date_w_demographics, end=date).astype(str).to_list()
    date_rows = []
    for row_date in date_list:
        url = 'https://www.doh.wa.gov/Emergencies/Coronavirus'

        # Washington's servers will not return a full HTML page
        # when requesting from Python (even with spoofed headers)
        # However, we can fetch the data from directly 
        # from https://github.com/lazd/coronadatascraper-cache
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        url_hash = m.hexdigest()
        row_date_obj = dparser.parse(row_date)
        cds_date = f'{row_date_obj.year}-{row_date_obj.month}-{row_date_obj.day}'
        cds_cache_url = f'https://github.com/lazd/coronadatascraper-cache/raw/master/{cds_date}/{url_hash}.html'
        print(cds_cache_url)
        raw = fetch(cds_cache_url, date=row_date, time_travel=True)

        if not raw:
            print(f'Could not pull data for {state}: {row_date}')
            print('NB: coronadatascraper-cache is not updated until at 9pm PST for that days data.')
            continue

    # Process raw data for all dates that have been downloaded
    
    

if __name__=='__main__':
    run_WA({})
    

