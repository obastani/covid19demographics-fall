# https://coronavirus.iowa.gov/

import csv
from datetime import datetime
import json
import os
import requests

def run_IA(args):
    # Parameters
    raw_name = '../IA/raw'
    data_name = '../IA/data/data.csv'
    now = str(datetime.now())
    
    out = {}
    pulls = [("Total_Cases", "TotalCases"), ("Male_Cases", "TotalMaleCases"), ("Female_Cases", "TotalFemaleCases"), ("Child_0_17", "Cases_0_17"), ("Adult_18_40", "Cases_18_40"), ("Middle_Age_41_60", "Cases_41_60"), ("Older_Adult_61_80", "Cases_61_80"), ("Elderly_81", "Cases_81_plus"), ("CurrHospitalized", "CurrHospitalized"), ("DischRecov", "DischargedRecovering"), ("Deceased", "Deceased")]
    for them, us in pulls:
        raw = requests.get("https://services.arcgis.com/vPD5PVLI6sfkZ5E4/arcgis/rest/services/IACOVID19Cases_Demographics/FeatureServer/0/query?f=json&where=1%3D1&outFields=*&returnGeometry=false&outStatistics=%5B%7B%22onStatisticField%22%3A%22" + them + "%22%2C%22outStatisticFieldName%22%3A%22" + them + "_sum%22%2C%22statisticType%22%3A%22sum%22%7D%5D").json()
        with open("%s/%s_%s.json" % (raw_name, us, now), "w") as fp:
            json.dump(raw, fp)
        out[us] = int(raw["features"][0]["attributes"]["%s_sum" % them])
    out["Scrape_Time"] = now

    fields = [x for x in out]
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])

if __name__ == '__main__':
    run_IA({})
