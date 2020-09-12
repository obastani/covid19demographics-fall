# https://www.arcgis.com/apps/MapSeries/index.html?appid=7c34f3412536439491adcc2103421d4b
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import json
import os
import re
import requests

def run_MT(args):
    # Parameters
    raw_name = '../MT/raw'
    county_data_name = '../MT/data/data_county.csv'
    state_data_name = '../MT/data/data_state.csv'
    case_data_name = '../MT/data/data_case.csv'
    now = str(datetime.now())

    raw = requests.get("https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/0/query?f=json&where=Total%20%3C%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=NewCases%20desc%2CNAMELABEL%20asc&outSR=102100&resultOffset=0&resultRecordCount=56&cacheHint=true").json()
    with open("%s/counties_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)

    cfields = ['NAMELABEL', 'ALLFIPS', 'LAST_UPDATE', 'Total', 'F_0_9', 'M_0_9', 'T_0_9', 'F_10_19', 'M_10_19', 'T_10_19', 'F_20_29', 'M_20_29', 'T_20_29', 'F_30_39', 'M_30_39', 'T_30_39', 'F_40_49', 'M_40_49', 'T_40_49', 'F_50_59', 'M_50_59', 'T_50_59', 'F_60_69', 'M_60_69', 'T_60_69', 'F_70_79', 'M_70_79', 'T_70_79', 'F_80_89', 'M_80_89', 'T_80_89', 'F_90_99', 'M_90_99', 'T_90_99', 'F_100', 'M_100', 'T_100', 'Notes', "Scrape_Time"]
    cinfo = []
    for x in raw["features"]:
        x = x["attributes"]
        x["Scrape_Time"] = now
        x["LAST_UPDATE"] = str(datetime.fromtimestamp(float(x["LAST_UPDATE"] / 1000.0)))
        cinfo.append([x[y] for y in cfields])
    exists = os.path.exists(county_data_name)
    with open(county_data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(cfields)
        for x in cinfo:
            writer.writerow(x)

    out = {}
    raw = requests.get("https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=ScriptRunDate%20desc&outSR=102100&resultOffset=0&resultRecordCount=1&cacheHint=true").json()
    with open("%s/tests_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    dat = raw["features"][0]["attributes"]
    out["TestDate"] = datetime.utcfromtimestamp(dat["Test_Date"]/1000).strftime("%Y-%m-%d")
    out["LastDayTestCount"] = dat["New_Tests_Completed"]
    out["OverallTestCount"] = dat["Total_Tests_Completed"]

    raw = requests.get("https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/2/query?f=json&where=(Hospitalization%3D%27Y%27%20OR%20Hospitalization%3D%27P%27)&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22count%22%2C%22onStatisticField%22%3A%22OBJECTID%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&cacheHint=true").json()
    with open("%s/totalhosp_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    out["TotalHospitalizations"] = int(raw["features"][0]["attributes"]["value"])

    raw = requests.get("https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/2/query?f=json&where=Hospitalization%3D%27Y%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22count%22%2C%22onStatisticField%22%3A%22OBJECTID%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&cacheHint=true").json()
    with open("%s/activehosp_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    out["ActiveHospitalizations"] = int(raw["features"][0]["attributes"]["value"])

    raw = requests.get("https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/0/query?f=json&where=Total%20%3C%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22NewCases%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&cacheHint=true").json()
    with open("%s/deaths_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    out["Deaths"] = int(raw["features"][0]["attributes"]["value"])

    raw = requests.get("https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/0/query?f=json&where=Total%20%3C%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Total%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&cacheHint=true").json()
    with open("%s/cc_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    out["ConfirmedCases"] = int(raw["features"][0]["attributes"]["value"])

    raw = requests.get("https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/0/query?f=json&where=Total%20%3C%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22TotalRecovered%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&cacheHint=true").json()
    with open("%s/recovered_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    out["Recovered"] = int(raw["features"][0]["attributes"]["value"])
    
    out["Scrape_Time"] = now

    fields = [x for x in out]
    exists = os.path.exists(state_data_name)
    with open(state_data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])

    raw = requests.get("https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/2/query?f=json&where=MT_case%3C%3E%27X%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Date_Reported_to_CDEpi%20asc&outSR=102100&resultOffset=0&resultRecordCount=2000&cacheHint=true").json()
    with open("%s/cases_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    cases = []
    fields = ["Case_No", "Date", "County", "Age_Group", "Sex", "Hospitalization", "Outcome", "MT_case", "Scrape_Time"]
    for x in raw["features"]:
        x = x["attributes"]
        x["Date"] = datetime.utcfromtimestamp(x["Date_Reported_to_CDEpi"]/1000).strftime("%Y-%m-%d")
        x["Scrape_Time"] = now
        cases.append([x[y] for y in fields])
        
    exists = os.path.exists(case_data_name)
    with open(case_data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        for x in cases:
            writer.writerow(x)
        
if __name__ == '__main__':
    run_MT({})
