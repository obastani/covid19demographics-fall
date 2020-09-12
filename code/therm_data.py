import pycurl 
import us, pdb

def get_therm_data(args):
    for state in us.states.mapping('abbr', 'name'):
        with open(f"therm_data/{state}_data.json", 'wb') as fp:
            crl = pycurl.Curl() 
            crl.setopt(crl.URL, f'https://static.kinsahealth.com/{state}_data.json')
            crl.setopt(crl.WRITEDATA, fp)
            crl.perform() 
            crl.close()

if __name__=="__main__":
    get_therm_data({})

