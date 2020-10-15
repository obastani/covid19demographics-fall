from helpers.alex import *

date = datetime.date.today().strftime('%Y-%m-%d')
state = 'MO'

def fetch(url, **kwargs):
    if 'date' not in kwargs.keys() or kwargs['date']==False:
        kwargs['date'] = date
    if 'state' not in kwargs.keys() or kwargs['state']==False:
        kwargs['state'] = state
    return(fetch_(url, **kwargs))

def run_MO(args):
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


    print('Downloading MO raw data... (needs to be extracted to CSV).')
    R = fetch("https://results.mo.gov/vizql/t/COVID19/w/Demographics/v/Public-Demographics/bootstrapSession/sessions/1E648FE2A68E4FEF8BC7B7D6080015C4-2:3",
      method='POST',
      headers={
        "accept": "text/javascript",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-tsi-active-tab": "Public%20-%20Demographics",
        "referrer": "https://results.mo.gov/t/COVID19/views/Demographics/Public-Demographics?:embed=y&:showVizHome=no&:host_url=https%3A%2F%2Fresults.mo.gov%2F&:embed_code_version=3&:tabs=no&:toolbar=no&:showAppBanner=false&:%E2%80%98iframeSizedToWindow%E2%80%99=%E2%80%98true%E2%80%99&:dataDetails=no&:display_spinner=no&:loadOrderID=0",
        "referrerPolicy": "no-referrer-when-downgrade"
      },
      payload="worksheetPortSize=%7B%22w%22%3A1100%2C%22h%22%3A1301%7D&dashboardPortSize=%7B%22w%22%3A1100%2C%22h%22%3A1301%7D&clientDimension=%7B%22w%22%3A520%2C%22h%22%3A1327%7D&renderMapsClientSide=true&isBrowserRendering=true&browserRenderingThreshold=100&formatDataValueLocally=false&clientNum=&navType=Nav&navSrc=Boot&devicePixelRatio=1.7999999523162842&clientRenderPixelLimit=25000000&allowAutogenWorksheetPhoneLayouts=false&sheet_id=Public%2520-%2520Demographics&showParams=%7B%22checkpoint%22%3Afalse%2C%22refresh%22%3Afalse%2C%22refreshUnmodified%22%3Afalse%2C%22unknownParams%22%3A%22%3Aembed_code_version%3D3%26%3A%25E2%2580%2598iframeSizedToWindow%25E2%2580%2599%3D%25E2%2580%2598true%25E2%2580%2599%22%7D&stickySessionKey=%7B%22dataserverPermissions%22%3A%2244136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a%22%2C%22featureFlags%22%3A%22%7B%7D%22%2C%22isAuthoring%22%3Afalse%2C%22isOfflineMode%22%3Afalse%2C%22lastUpdatedAt%22%3A1602715073645%2C%22viewId%22%3A91%2C%22workbookId%22%3A20%7D&filterTileSize=200&locale=en_US&language=en&verboseMode=false&%3Asession_feature_flags=%7B%7D&keychain_version=1"
    )


if __name__=="__main__":
    run_MO({})
    
