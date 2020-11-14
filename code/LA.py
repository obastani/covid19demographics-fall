# http://ldh.la.gov/coronavirus/
import csv
from datetime import datetime
import json
import os
from urllib.request import urlopen, Request
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from johnutil.imgutil import getGraph, getCanvas
import re
import time
from bs4 import BeautifulSoup
import pandas as pd

def merge_parish():
    path = '../LA/data'

    all_records = []
    keys = set()

    for file in os.listdir(path):
        if "parish" in file:
            df = pd.read_csv(path + "/" + file)
            cols = df.columns
            for col in cols:
                keys.add(col)
            records = df.to_dict('records')            
            all_records.extend(records)
    
    keys = list(keys)
    
    out_path = '../LA/data/merged_parish_race.csv'

    if os.path.exists(out_path):
        os.remove(out_path)

    for record in all_records:
        fields = sorted([x for x in keys])
        exists = os.path.exists(out_path)
        with open(out_path, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            row = []
            for key in fields:
                try:
                    val = record[key]
                except:
                    val = None
                row.append(val)
            writer.writerow(row)

def run_LA(args):

    # Parameters
    raw_name = '../LA/raw'
    data_name = '../LA/data/data.csv'
    parish_race_name = '../LA/data/parish_race_data.csv'
    now = str(datetime.now())

    fulldat = {}
    raw = requests.get("https://services5.arcgis.com/O5K6bb5dZVZcTo5M/arcgis/rest/services/Combined_COVID_Reporting/FeatureServer/0/query?f=json&where=Measure%3D%27Age%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Group_Num%2CValueType&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Value%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true").json()
    with open("%s/age_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    groups_death = ["%s_0_17", "%s_18_29", "%s_30_39", "%s_40_49", "%s_50_59", "%s_60_69", "%s_70_plus"]
    groups_case = ["%s_0_4", "%s_5_17", "%s_18_29", "%s_30_39", "%s_40_49", "%s_50_59", "%s_60_69", "%s_70_plus"] 
    if len(raw["features"]) != 15:
        raise Exception("Unexpected number of ages in LA: " + str(len(raw["features"])))
    
    raw_cases = []
    raw_deaths = []
    for entry in raw["features"]:
        if entry["attributes"]["ValueType"] == "case":
            raw_cases.append(entry["attributes"])
        else:
            raw_deaths.append(entry["attributes"])
    if len(raw_cases) != 8:
        raise Exception("Unexpected number of entries for age cases: " + str(len(raw_cases)))
    if len(raw_deaths) != 7:
        raise Exception("Unexpected number of entries for age deaths: " + str(len(raw_deaths)))

    for apos in range(8):
        fulldat[groups_case[apos] % "Case"] = raw_cases[apos]["value"]
    for apos in range(7):
        fulldat[groups_death[apos] % "Deaths"] = raw_deaths[apos]["value"]

    # for apos in range(8):
    #     for atype, aname in [("case", "Cases"), ("death", "Deaths")]:
    #         print(len(raw["features"]))
    #         exit()
    #         dat = [x["attributes"] for x in raw["features"] if x["attributes"]["Group_Num"] == apos+1 and x["attributes"]["ValueType"] == atype]
    #         if len(dat) != 1:
    #             print(dat)
    #             raise Exception("Missing some age data")
    #         if atype == "case":
    #             fulldat[groups_case[apos] % aname] = dat[0]["value"]
    #         else:
    #             fulldat[groups_death[apos] % aname] = dat[0]["value"]


    raw = requests.get("https://services5.arcgis.com/O5K6bb5dZVZcTo5M/arcgis/rest/services/Combined_COVID_Reporting/FeatureServer/0/query?f=json&where=Measure%3D%27Gender%27%20AND%20ValueType%3D%27case%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Group_Num&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Value%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true").json()
    with open("%s/gender_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    if len(raw["features"]) != 3:
        raise Exception("Unexpected number of genders in LA")
    groups = [(1, "Case_Pct_Male"), (2, "Case_Pct_Female"), (3, "Case_Pct_Other")]
    for gnum, name in groups:
        dat = [x["attributes"] for x in raw["features"] if x["attributes"]["Group_Num"] == gnum]
        if len(dat) != 1:
            raise Exception("Missing some gender data")
        fulldat[name] = dat[0]["value"]

    raw = requests.get("https://services5.arcgis.com/O5K6bb5dZVZcTo5M/arcgis/rest/services/Combined_COVID_Reporting/FeatureServer/0/query?f=json&where=Measure%3D%27State%20Tests%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Value%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true").json()
    with open("%s/statelab_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    fulldat["TestsByStateLab"] = int(raw["features"][0]["attributes"]["value"])

    raw = requests.get("https://services5.arcgis.com/O5K6bb5dZVZcTo5M/arcgis/rest/services/Combined_COVID_Reporting/FeatureServer/0/query?f=json&where=Measure%3D%27Commercial%20Tests%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Value%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true").json()
    with open("%s/commercial_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    fulldat["CommercialTests"] = int(raw["features"][0]["attributes"]["value"])

    # raw = requests.get("https://www.arcgis.com/sharing/rest/content/items/69b726e2b82e408f89c3a54f96e8f776/data?f=json").json()
    # with open("%s/hospital_%s.json" % (raw_name, now), "w") as fp:
    #     json.dump(raw, fp)
    # hospInfo = [x for x in raw["widgets"] if "defaultSettings" in x and "bottomSection" in x["defaultSettings"] and "textInfo" in x["defaultSettings"]["bottomSection"] and "text" in x["defaultSettings"]["bottomSection"]["textInfo"] and "ventilators" in x["defaultSettings"]["bottomSection"]["textInfo"]["text"]]
    # if len(hospInfo) != 1:
    #     raise Exception("Bad ventilator layout in LA")
    # fulldat["OnVentilator"] = int(hospInfo[0]["defaultSettings"]["bottomSection"]["textInfo"]["text"].split()[0])
    # ds = [x for x in hospInfo[0]["datasets"] if x["type"] == "staticDataset" and x["name"] == "reference"]
    # if len(ds) != 1:
    #     raise Exception("Bad hospitalized layout")
    # fulldat["Hospitalized"] = int(ds[0]["data"])
    fulldat["Scrape_Time"] = now

    raw = requests.get("https://services5.arcgis.com/O5K6bb5dZVZcTo5M/arcgis/rest/services/Combined_COVID_Reporting/FeatureServer/0/query?f=json&where=Measure%3D%27Beds%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Geography%2CGroup_Num&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Value%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true").json()    
    with open("%s/bedsbyregion_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    if len(raw["features"]) != 18:
        raise Exception("Unexpected number of bed/regions in LA")
    for region in range(1, 10):
        for gnum, cat in [(1, "InUse"), (2, "StillAvailable")]:
            dat = [x["attributes"] for x in raw["features"] if x["attributes"]["Geography"] == "LDH Region %d" % region and x["attributes"]["Group_Num"] == gnum]
            if len(dat) != 1:
                raise Exception("Bad bed/region")
            fulldat["Beds_" + cat + "Region" + str(region)] = dat[0]["value"]

    raw = requests.get("https://services5.arcgis.com/O5K6bb5dZVZcTo5M/arcgis/rest/services/Combined_COVID_Reporting/FeatureServer/0/query?f=json&where=Measure%3D%27ICU%20Beds%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Geography%2CGroup_Num&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Value%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true").json()
    with open("%s/ICUbedsbyregion_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    if len(raw["features"]) != 18:
        raise Exception("Unexpected number of ICU bed/regions in LA")
    for region in range(1, 10):
        for gnum, cat in [(1, "InUse"), (2, "StillAvailable")]:
            dat = [x["attributes"] for x in raw["features"] if x["attributes"]["Geography"] == "LDH Region %d" % region and x["attributes"]["Group_Num"] == gnum]
            if len(dat) != 1:
                raise Exception("Bad ICU bed/region")
            fulldat["ICUBeds_" + cat + "Region" + str(region)] = dat[0]["value"]

    raw = requests.get("https://services5.arcgis.com/O5K6bb5dZVZcTo5M/arcgis/rest/services/Combined_COVID_Reporting/FeatureServer/0/query?f=json&where=Measure%3D%27Hospital%20Vents%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Geography%2CGroup_Num&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Value%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true").json()
    with open("%s/ventbyregion_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    if len(raw["features"]) != 18:
        raise Exception("Unexpected number of ventilator/regions in LA")
    for region in range(1, 10):
        for gnum, cat in [(1, "InUse"), (2, "StillAvailable")]:
            dat = [x["attributes"] for x in raw["features"] if x["attributes"]["Geography"] == "LDH Region %d" % region and x["attributes"]["Group_Num"] == gnum]
            if len(dat) != 1:
                raise Exception("Bad ventilator/region")
            fulldat["Vent_" + cat + "Region" + str(region)] = dat[0]["value"]
    
    # New data - Race by region
    raw = requests.get('https://services5.arcgis.com/O5K6bb5dZVZcTo5M/arcgis/rest/services/Case_Deaths_Race_Region_new/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=LDH_Region%2CRace&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true').json()
    with open("%s/DeathRacebyRegion_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    race_data = raw["features"]
    if len(race_data) != 63:
        raise Exception("Unexpected number of regions/races")
    expected_regions = ["Region 1", "Region 2", "Region 3", "Region 4", "Region 5", "Region 6", "Region 7", "Region 8", "Region 9"]
    expected_races = ["White", "Black", "Unknown", "Asian", "Native Hawaiian/Other Pacific Islander", "American Indian/Alaskan Native", "Other"]
    for attribute in race_data:
        race_data = attribute["attributes"]
        if race_data["LDH_Region"] not in expected_regions:
            raise Exception("Unexpeted region " + race_data["LDH_Region"])
        if race_data["Race"] not in expected_races:
            raise Exception("Unexpected race " + race_data["Race"])
        fulldat["Deaths_" + race_data["LDH_Region"].strip() + "_race_" + race_data["Race"]] = race_data["value"]

    #Case Race by region
    raw = requests.get('https://services5.arcgis.com/O5K6bb5dZVZcTo5M/arcgis/rest/services/Case_Deaths_Race_Region_new/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=LDH_Region%2CRace&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Cases%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true').json()
    with open("%s/CaseRacebyRegion_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    race_data = raw["features"]
    if len(race_data) != 63:
        raise Exception("Unexpected number of regions/races")
    expected_regions = ["Region 1", "Region 2", "Region 3", "Region 4", "Region 5", "Region 6", "Region 7", "Region 8", "Region 9"]
    expected_races = ["White", "Black", "Unknown", "Asian", "Native Hawaiian/Other Pacific Islander", "American Indian/Alaskan Native", "Other"]
    for attribute in race_data:
        race_data = attribute["attributes"]
        if race_data["LDH_Region"] not in expected_regions:
            raise Exception("Unexpeted region " + race_data["LDH_Region"])
        if race_data["Race"] not in expected_races:
            raise Exception("Unexpected race " + race_data["Race"])
        fulldat["Casess_" + race_data["LDH_Region"].strip() + "_race_" + race_data["Race"]] = race_data["value"]

    # New data - Race by parish
    out_parish = []
    raw = requests.get('https://services5.arcgis.com/O5K6bb5dZVZcTo5M/arcgis/rest/services/Cases_and_Deaths_by_Race_by_Parish_and_Region/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=65&resultType=standard&cacheHint=true').json()
    with open("%s/RacebyParish_%s.json" % (raw_name, now), "w") as fp:
        json.dump(raw, fp)
    race_parish_data = raw["features"]
    expected_races = ["White", "Black", "Unknown", "Asian", "Native_Hawaiian_Other_Pacific_Islander", "American_Indian_Alaskan_Native", "Other"]
    for row in race_parish_data:
        parish_data = row["attributes"]
        parish_dict = {
            "Parish": parish_data["Parish"],
            "Scrape Time": now
        }
        for key in parish_data:
            if "Deaths_" in key:
                val = parish_data[key]
                if val == "":
                    val = 0
                parish_dict[key + "_race"] = val
            elif "Cases_" in key:
                val = parish_data[key]
                if val == "":
                    val = 0
                parish_dict[key + "_race"] = val
            elif "LDHH" in key:
                parish_dict[key] = parish_data[key]
        # for race in expected_races:
            # try:
            #     parish_dict["Deaths_Race_" + race] = parish_data[race]
            # except:
            #     print("Unexpected race: " + race)
            #     raise
        out_parish.append(parish_dict)

    # Tableau - Probable Deaths 
   

    # Using Selenium
    # driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get("https://public.tableau.com/profile/lee.mendoza#!/vizhome/COVID19demog/DataonCOVIN-19RelatedDeathsToDate")
    time.sleep(5)
    # Get raw
    driver.save_screenshot(raw_name + "/probable_deaths_pt1_" + now + ".png")
    driver.execute_script("window.scrollTo(0, 400)")
    driver.save_screenshot(raw_name + "/probable_deaths_pt2_" + now + ".png")

    frame = driver.find_element_by_xpath('//*[@id="ng-app"]/body/div[1]/div[2]/section/div/div[2]/section[2]/figure/js-api-viz/div/iframe')
    driver.switch_to.frame(frame)
   
    # # Total Probable Deaths
    # total_prob_deaths = driver.find_element_by_xpath('//*[@id="tabZoneId19"]/div/div/div/div[1]/div/span/div[1]/span').text
    # total_prob_deaths_num = re.sub('[^0-9]', '', total_prob_deaths)
    # fulldat["Total Probable Deaths"] = total_prob_deaths_num

    # Probable Deaths by Race
    headers_race = driver.find_element_by_xpath('//*[@id="tabZoneId3"]/div/div/div/div[1]/div[5]/div[1]/canvas')
    values_race = driver.find_element_by_xpath('//*[@id="view13678703414402932068_2418008377866606056"]/div[1]/div[2]/canvas[1]')

    head = getCanvas(headers_race, driver).replace("\n\n", "\n")
    val = getCanvas(values_race, driver).replace("\n\n", "\n")

    expected_race = ["American Indian/Alaska N..", "Asian",  "Black",  "Native Hawaiian/Pl", "Other",  "Unknown",  "White"]
    extracted_races = []
    for line in head.splitlines():
        if line != "\n" or line != "":
            extracted_races.append(line)
    for race, pct in zip(extracted_races, val.splitlines()):
        percent = pct.replace("%", "")
        if race.strip() == "Native Hawaiian/PI":
            race = "Native Hawaiian/Pl"
        if race.strip() not in expected_race:
            raise Exception("Unexpected race in Probable Deaths " + race)
        fulldat["% Probable Deaths by Race: " + race] = percent
    
    # Probable Deaths by Ethnicity
    headers_ethnicity = driver.find_element_by_xpath('//*[@id="tabZoneId10"]/div/div/div/div[1]/div[5]/div[1]/canvas')
    values_ethnicity = driver.find_element_by_xpath('//*[@id="view13678703414402932068_2377024103324179123"]/div[1]/div[2]/canvas[1]')

    head = getCanvas(headers_ethnicity, driver).replace("\n\n", "\n")
    val = getCanvas(values_ethnicity, driver).replace("\n\n", "\n")
    expected_ethn = ["Hispanic/Latino", "Non-Hispanic/Latino", "Unknown"]
    for ethn, pct in zip(head.splitlines(), val.splitlines()):
        if ethn.strip() not in expected_ethn:
            raise Exception("Unexpected Ethnicity " + ethn)
        percent = pct.replace("%","")
        fulldat["% Probable Deaths by Ethnicity: " + ethn] = percent
    # Probable Deaths by Gender
    headers_gender = driver.find_element_by_xpath('//*[@id="tabZoneId18"]/div/div/div/div[1]/div[5]/div[1]/canvas')
    values_gender = driver.find_element_by_xpath('//*[@id="view13678703414402932068_1339666610323305087"]/div[1]/div[2]/canvas[1]')

    head = getCanvas(headers_gender, driver).replace("\n\n", "\n")
    val = getCanvas(values_gender, driver).replace("\n\n", "\n")
    expected_gender = ["Female", "Male", "Unknown/Other"]
    for gen, pct in zip(head.splitlines(), val.splitlines()):
        if gen.strip() not in expected_gender:
            raise Exception("Unexpected Gender " + gen)
        percent = pct.replace("%","")
        fulldat["% Probable Deaths by Gender: " + gen] = percent
    
    # Probable Deaths by Underlying Conditions
    headers_conditions = driver.find_element_by_xpath('//*[@id="tabZoneId5"]/div/div/div/div[1]/div[5]/div[1]/canvas')
    values_conditions = driver.find_element_by_xpath('//*[@id="view13678703414402932068_5659047270258252395"]/div[1]/div[2]/canvas[1]')

    head = getCanvas(headers_conditions, driver).replace("\n\n", "\n")
    val = getCanvas(values_conditions, driver).replace("\n\n", "\n")
    expected_conditions = [ "Asthma",
                            "Cancer",
                            "Cardiac Disease",
                            "Chronic Kidney Disease",
                            "Congestive Heart Failure",
                            "Diabetes",
                            "Hypertension",
                            "Neurological",
                            "Obesity",
                            "Pulmonary",
                            "None"]
    for con, pct in zip(head.splitlines(), val.splitlines()):
        if con.strip() not in expected_conditions:
            raise Exception("Unexpected Underlying Condition " + con)
        percent = pct.replace("%","")
        fulldat["% Probable Deaths by Underlying Condition: " + con] = percent              
    
    # Probable Deaths - Avg and Median Ages
    headers_age = driver.find_element_by_xpath('//*[@id="tabZoneId21"]/div/div/div/div[1]/div[5]/div[1]/canvas')
    values_age = driver.find_element_by_xpath('//*[@id="view13678703414402932068_10330976522668559202"]/div[1]/div[2]/canvas[1]')

    head = getCanvas(headers_age, driver).replace("\n\n", "\n")
    val = getCanvas(values_age, driver).replace("\n\n", "\n")
    expected_metrics = ["Average", "Median"]

    for metric, age in zip(head.splitlines(), val.splitlines()):
        if metric.strip() not in expected_metrics:
            raise Exception("Unexpected Age Metric " + con)
        fulldat["Probable Deaths Age: " + metric] = age
 
    # Output
    fields = sorted([x for x in fulldat])
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([fulldat[x] for x in fields])

    # Output - Parish
    for parish in out_parish:
        fields = sorted([x for x in parish])
        exists = os.path.exists(parish_race_name)
        with open(parish_race_name, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([parish[x] for x in fields])
    
    # Merge Parish Race data
    merge_parish()

if __name__ == '__main__':
    run_LA({})
