# To scrape: https://experience.arcgis.com/experience/96dd742462124fa0b38ddedb9b25e429/
import csv
from datetime import datetime
import json
import os
import requests

def run_FL(args):
    # Parameters
    raw_name = '../FL/raw'
    data_name = '../FL/data/data.csv'
    zipdata_name = '../FL/data/zipdata.csv'
    now = str(datetime.now())

    raw = requests.get("https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/Florida_COVID19_Cases/FeatureServer/0/query?f=json&where=County_1%20IS%20NOT%20NULL&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=County_1%20asc&outSR=102100&resultOffset=0&resultRecordCount=70").json()
    with open("%s/%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)

    fields = ['COUNTY', 'COUNTYNAME', 'PUIsTotal', 'Age_0_4', 'Age_5_14', 'Age_15_24', 'Age_25_34', 'Age_35_44', 'Age_45_54', 'Age_55_64', 'Age_65_74', 'Age_75_84', 'Age_85plus', 'Age_Unkn', 'PUIAgeRange', 'PUIAgeMedian', 'PUIFemale', 'PUIMale', 'PUISexUnkn', 'PUIFLRes', 'PUINotFLRes', 'PUIFLResOut', 'PUIContNo', 'PUIContUnkn', 'PUITravelNo', 'PUITravelYes', 'TPositive', 'TNegative', 'TInconc', 'TPending', 'T_Total_Res', 'C_Female', 'C_Male', 'C_SexUnkn', 'C_AllResTypes', 'C_Age_0_4', 'C_Age_5_14', 'C_Age_15_24', 'C_Age_25_34', 'C_Age_35_44', 'C_Age_45_54', 'C_Age_55_64', 'C_Age_65_74', 'C_Age_75_84', 'C_Age_85plus', 'C_Age_Unkn', 'C_AgeRange', 'C_AgeMedian', 'C_RaceWhite', 'C_RaceBlack', 'C_RaceOther', 'C_RaceUnknown', 'C_HispanicYES', 'C_HispanicNO', 'C_HispanicUnk', 'C_EDYes_Res', 'C_EDYes_NonRes', 'C_HospYes_Res', 'C_HospYes_NonRes', 'C_NonResDeaths', 'C_FLResDeaths', 'CasesAll', 'C_Men', 'C_Women', 'C_FLRes', 'C_NotFLRes', 'C_FLResOut', 'T_NegRes', 'T_NegNotFLRes', 'T_total', 'T_negative', 'T_positive', 'Deaths', 'EverMon', 'MonNow', "Scrape_Time"]
    res = []
    for x in raw["features"]:
        x = x["attributes"]
        x["Scrape_Time"] = now
        res.append([x[y] for y in fields])

    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        for row in res:
            writer.writerow(row)

    zipraw = requests.get("https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/Florida_Cases_Zips_COVID19/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=COUNTYNAME%20asc&resultOffset=0&resultRecordCount=1200&resultType=standard&cacheHint=true").json()
    with open("%s/zip_%s.json" % (raw_name, now), "w") as fp:
        json.dump(zipraw, fp)
    fields = ['COUNTY', 'COUNTYNAME', 'ZIP', 'NAME', 'Cases_1', "Scrape_Time"]
    zipres = []
    # print(zipraw)
    for x in zipraw["features"]:
        x = x["attributes"]
        x["Scrape_Time"] = now
        if not "COUNTY" in x:
            x["COUNTY"] = None
        if not "NAME" in x:
            x["NAME"] = x["c_places"]
        if not "Cases_1" in x:
            x["Cases_1"] = x["Cases"]
        zipres.append([x[y] for y in fields])

    exists = os.path.exists(zipdata_name)
    with open(zipdata_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        for row in zipres:
            writer.writerow(row)

if __name__ == '__main__':
    run_FL({})
