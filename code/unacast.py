# https://www.unacast.com/covid19/social-distancing-scoreboard

import csv
from datetime import datetime
import requests
import time

def run_unacast():
    # Parameters
    data_name = '../unacast/data'
    now = str(datetime.now())

    # http://code.activestate.com/recipes/577775-state-fips-codes-dict/
    state_codes = {
        'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15',
        'FL': '12', 'WY': '56', 'NJ': '34', 'NM': '35', 'TX': '48',
        'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36',
        'PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
        'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13',
        'IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
        'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29',
        'MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
        'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'
    }
    removed = {'PR': '72', "AS": "60", "MP": "69", "VI": "78", "GU": "66"}

    expect = ["date", "visitationGrade", "totalGrade", "visitationGradeBucket", "travelDistanceMetric", "travelDistanceGrade",
              "visitationMetric", "travelDistanceGradeBucket", "encountersGrade", "encountersGradeBucket", "encountersMetric"]
    fulldat = []
    for state, fips in state_codes.items():
        print("Processing", state)
        url = "https://covid19-scoreboard-api.unacastapis.com/api/search/covidcountyaggregates_v3?q=stateFips:" + fips + "&size=4000"
        dat = requests.get(url).json()
        for county in dat["hits"]["hits"]:
            for date in county["_source"]["data"]:
                if len(date.keys()) != len(expect) or not all([x in date for x in expect]):
                    raise Exception("Unexpected fields for county-date data")
                date["countyFips"] = county["_source"]["countyFips"]
                date["Scrape_Time"] = now
                fulldat.append(date)
        time.sleep(3.0)

    # Output
    fields = [x for x in fulldat[0]]
    with open("%s/%s.csv" % (data_name, now), "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(fields)
        for dat in fulldat:
            writer.writerow([dat[x] for x in fields])

if __name__ == '__main__':
    run_unacast()

