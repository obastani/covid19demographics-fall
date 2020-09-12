from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import re
import sys
from urllib.request import urlopen
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
import json
import os

def run_AR(args):
    # Parameters
    raw_name = '../AR/raw'
    data_name = '../AR/data/data.csv'
    data_county = '../AR/data/data_county.csv'
    main_url = 'https://www.healthy.arkansas.gov/programs-services/topics/novel-coronavirus'
    arcgis_url = 'https://adem.maps.arcgis.com/apps/opsdashboard/index.html#/1d80295a97054631a5c35d0556803f16'
    now = str(datetime.now())
   
    # Get hospitalized and ventilator data from html
    html = urlopen("https://www.healthy.arkansas.gov/programs-services/topics/novel-coronavirus").read()
    soup = BeautifulSoup(html, "html.parser")
    g = open('{}/{}.html'.format(raw_name, now), 'w')
    g.write(str(soup))
    g.close()

    # Output data structure
    out = {}

    # Get currently hospitalized, ventilated and nursing home patients
    # try:
    #     hosp = int(list(list(soup(text="Currently Hospitalized")[0].parent.parent.children)[3].children)[0].replace(',', ''))
    #     vent = int(list(list(soup(text="Currently on Ventilator")[0].parent.parent.children)[3].children)[0].replace(',', ''))
    #     nurs = int(list(list(soup(text="Total Nursing Home Residents")[0].parent.parent.children)[3].children)[0].replace(',', ''))
    # except:
    #     print('Unexpected text for hospitalized, ventilator and nursing')
    #     raise

    # out["Total Hospitalized"] = hosp
    # out["On Ventilator"] = vent
    # out["Nursing Home Patients"] = nurs

    # arcgis links
    total_cases_link = 'https://services.arcgis.com/PwY9ZuZRDiI5nXUB/arcgis/rest/services/ADH_COVID19_Positive_Test_Results/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22positive%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
    active_cases_link = 'https://services.arcgis.com/PwY9ZuZRDiI5nXUB/arcgis/rest/services/ADH_COVID19_Positive_Test_Results/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22active_cases%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
    total_deaths_link = 'https://services.arcgis.com/PwY9ZuZRDiI5nXUB/arcgis/rest/services/ADH_COVID19_Positive_Test_Results/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
    total_recoveries_link = 'https://services.arcgis.com/PwY9ZuZRDiI5nXUB/arcgis/rest/services/ADH_COVID19_Positive_Test_Results/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Recoveries%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
    county_link = 'https://services.arcgis.com/PwY9ZuZRDiI5nXUB/arcgis/rest/services/ADH_COVID19_Positive_Test_Results/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=county_nam%20asc&outSR=102100&resultOffset=0&resultRecordCount=80&resultType=standard&cacheHint=true'
    healthcare_link = 'https://services.arcgis.com/PwY9ZuZRDiI5nXUB/arcgis/rest/services/ADH_COVID19_State_Case_Metrics/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22nursing_home%22%2C%22outStatisticFieldName%22%3A%22nursing_home%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22diabetes%22%2C%22outStatisticFieldName%22%3A%22diabetes%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22cardiac_disease%22%2C%22outStatisticFieldName%22%3A%22cardiac_disease%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22hypertension%22%2C%22outStatisticFieldName%22%3A%22hypertension%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22cpd%22%2C%22outStatisticFieldName%22%3A%22cpd%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22ckd%22%2C%22outStatisticFieldName%22%3A%22ckd%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22immunocompromised%22%2C%22outStatisticFieldName%22%3A%22immunocompromised%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22healthcare%22%2C%22outStatisticFieldName%22%3A%22healthcare%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true'
    case_link = 'https://services.arcgis.com/PwY9ZuZRDiI5nXUB/arcgis/rest/services/ADH_COVID19_State_Case_Metrics/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22hispanic%22%2C%22outStatisticFieldName%22%3A%22hispanic%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22nonhispanic%22%2C%22outStatisticFieldName%22%3A%22nonhispanic%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22age_1%22%2C%22outStatisticFieldName%22%3A%22age_1%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22age_2%22%2C%22outStatisticFieldName%22%3A%22age_2%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22age_3%22%2C%22outStatisticFieldName%22%3A%22age_3%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22age_4%22%2C%22outStatisticFieldName%22%3A%22age_4%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22age_5%22%2C%22outStatisticFieldName%22%3A%22age_5%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22male%22%2C%22outStatisticFieldName%22%3A%22male%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22female%22%2C%22outStatisticFieldName%22%3A%22female%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22white%22%2C%22outStatisticFieldName%22%3A%22white%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22black%22%2C%22outStatisticFieldName%22%3A%22black%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22na%22%2C%22outStatisticFieldName%22%3A%22na%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22asian%22%2C%22outStatisticFieldName%22%3A%22asian%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22pi%22%2C%22outStatisticFieldName%22%3A%22pi%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22unk_race%22%2C%22outStatisticFieldName%22%3A%22unk_race%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true'
    death_race_link = 'https://services.arcgis.com/PwY9ZuZRDiI5nXUB/arcgis/rest/services/ADH_COVID19_State_Case_Metrics/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22d_white%22%2C%22outStatisticFieldName%22%3A%22d_white%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22d_black%22%2C%22outStatisticFieldName%22%3A%22d_black%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22d_na%22%2C%22outStatisticFieldName%22%3A%22d_na%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22d_asian%22%2C%22outStatisticFieldName%22%3A%22d_asian%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22d_pi%22%2C%22outStatisticFieldName%22%3A%22d_pi%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22d_other_race%22%2C%22outStatisticFieldName%22%3A%22d_other_race%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true'
    death_ethn_link = 'https://services.arcgis.com/PwY9ZuZRDiI5nXUB/arcgis/rest/services/ADH_COVID19_State_Case_Metrics/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22d_hispanic%22%2C%22outStatisticFieldName%22%3A%22d_hispanic%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22d_nonhispanic%22%2C%22outStatisticFieldName%22%3A%22d_nonhispanic%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true'
    death_age_link = 'https://services.arcgis.com/PwY9ZuZRDiI5nXUB/arcgis/rest/services/ADH_COVID19_State_Case_Metrics/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22avg%22%2C%22onStatisticField%22%3A%22d_age_1%22%2C%22outStatisticFieldName%22%3A%22d_age_1%22%7D%2C%7B%22statisticType%22%3A%22avg%22%2C%22onStatisticField%22%3A%22d_age_2%22%2C%22outStatisticFieldName%22%3A%22d_age_2%22%7D%2C%7B%22statisticType%22%3A%22avg%22%2C%22onStatisticField%22%3A%22d_age_3%22%2C%22outStatisticFieldName%22%3A%22d_age_3%22%7D%2C%7B%22statisticType%22%3A%22avg%22%2C%22onStatisticField%22%3A%22d_age_4%22%2C%22outStatisticFieldName%22%3A%22d_age_4%22%7D%2C%7B%22statisticType%22%3A%22avg%22%2C%22onStatisticField%22%3A%22d_age_5%22%2C%22outStatisticFieldName%22%3A%22d_age_5%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true'
    # Cases
    # Total Cases number
    total_cases_raw = requests.get(total_cases_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_total_cases"), "w") as fp:
        json.dump(total_cases_raw, fp)
    # Process
    try:
        out["Total Cases"] = total_cases_raw["features"][0]["attributes"]["value"]
    except:
        print("Unexpected Total Cases Value")
        raise  
    # Active Cases
    active_cases_raw = requests.get(active_cases_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_active_cases"), "w") as fp:
        json.dump(active_cases_raw, fp)
    # Process
    try:
        out["Active Cases"] = active_cases_raw["features"][0]["attributes"]["value"]
    except:
        print("Unexpected Active Cases Value")
        raise 
    # Total Recoveries
    total_recoveries_raw = requests.get(total_recoveries_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_total_recoveries"), "w") as fp:
        json.dump(total_recoveries_raw, fp)
    # Process
    try:
        out["Total Recovered"] = total_recoveries_raw["features"][0]["attributes"]["value"]
    except:
        print("Unexpected Total Recovered Value")
        raise
    # All Cases data
    cases_raw = requests.get(case_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_cases"), "w") as fp:
        json.dump(cases_raw, fp)
    # Process
    values = cases_raw["features"][0]["attributes"]
    expected_fields = ["hispanic", "nonhispanic", "age_1", "age_2", "age_3",
                       "age_4", "age_5", "male", "female", "white", "black",
                       "na", "asian", "pi", "unk_race"]
    for key in values:
        if key not in expected_fields:
            raise Exception("Unexpected field in Cases")
        if "age" in key:
            if "1" in key:
                out['# Cases Age [0-17]'] = values[key]
            elif "2" in key:
                out['# Cases Age [18-24]'] = values[key]
            elif "3" in key:
                out['# Cases Age [25-44]'] = values[key]
            elif "4" in key:
                out['# Cases Age [45-64]'] = values[key]
            elif "5" in key:
                out['# Cases Age [65+]'] = values[key]
            else:
                raise Exception("Unexpected age in cases")
        elif "pi" in key:
            out["race_cases_pacificislander"] = values[key]
        elif "na" in key:
            out["race_cases_" + key] = values[key]
        else:
            out["cases_" + key] = values[key]
    # Healthcare data
    health_raw = requests.get(healthcare_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_health"), "w") as fp:
        json.dump(health_raw, fp)
    
    # # Process data
    values = health_raw["features"][0]["attributes"]
    expected_fields = ["nursing_home",
                       "diabetes","cardiac_disease","hypertension","cpd","ckd",
                       "immunocompromised","healthcare"]
    for key in values:
        if key not in expected_fields:
            raise Exception("Unexpected field in Hospital Cases")
        out["cases_" + key] = values[key]
    
    # Deaths
    # Total deaths number
    total_deaths_raw = requests.get(total_deaths_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_total_cases"), "w") as fp:
        json.dump(total_cases_raw, fp)
    # Process
    try:
        out["Total Deaths"] = total_deaths_raw["features"][0]["attributes"]["value"]
    except:
        print("Unexpected Total Deaths Value")
        raise  
    # Race
    death_race_raw = requests.get(death_race_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_death_race"), "w") as fp:
        json.dump(death_race_raw, fp)
    # Process
    values = death_race_raw["features"][0]["attributes"]
    expected_fields = ["d_white","d_black","d_na","d_asian","d_pi",
                       "d_other_race"]
    for key in values:
        if key not in expected_fields:
            raise Exception("Unexpected field in Race Death")
        if "pi" in key:
            out["Total Deaths: Pacific Islander"] = values[key]
        else:
            out["Total Deaths: " + key.replace("d_", "race_")] = values[key]
    # Ethnicity
    death_ethn_raw = requests.get(death_ethn_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_death_ethn"), "w") as fp:
        json.dump(death_ethn_raw, fp)
    # Process
    values = death_ethn_raw["features"][0]["attributes"]
    expected_fields = ["d_hispanic","d_nonhispanic"]
    for key in values:
        if key not in expected_fields:
            raise Exception("Unexpected field in Ethnicity Death")
        out["Total Deaths: " + key.replace("d_", "ethn_")] = values[key]
    # Age
    death_age_raw = requests.get(death_age_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_death_age"), "w") as fp:
        json.dump(death_age_raw, fp)
    # Process
    values = death_age_raw["features"][0]["attributes"]
    expected_fields = ["d_age_1","d_age_2","d_age_3","d_age_4","d_age_5"]
    for key in values:
        if key not in expected_fields:
            raise Exception("Unexpected field in Age Death")
        if "1" in key:
            out['# Deaths Age [0-17]'] = values[key]
        elif "2" in key:
            out['# Deaths Age [18-24]'] = values[key]
        elif "3" in key:
            out['# Deaths Age [25-44]'] = values[key]
        elif "4" in key:
            out['# Deaths Age [45-64]'] = values[key]
        elif "5" in key:
            out['# Deaths Age [65+]'] = values[key]
        else:
            raise Exception("Unexpected age in deaths")

    # County data
    out_county = []
    county_raw = requests.get(county_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_county"), "w") as fp:
        json.dump(county_raw, fp)
    values = county_raw["features"]
    for county in values:
        county_val = county["attributes"]
        try:
            county_data = {
                "County Name": county_val['county_nam'],
                "FIPS": county_val['FIPS'],
                "Positive Cases": county_val['positive'],
                "Negative Cases": county_val['negative'],
                "Pending Cases": county_val['pending'],
                "Testing: Private Lab": county_val['lab_prvt'],
                "Testing: Public Lab": county_val['lab_pub'],
                "Recovered": county_val['Recoveries'],
                "Deaths": county_val['deaths'],
                "Total Tested": county_val['total_tests'],
                "Active Cases": county_val['active_cases'],
                "Scrape Time": now
            }
        except:
            print("Missing County data field")
            raise
        out_county.append(county_data)
    
    # Output - all data
    out["Scrape_Time"] = now
    fields = sorted([x for x in out])
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])
    
    # Output - county
    for county in out_county:
        fields = sorted([x for x in county])
        exists = os.path.exists(data_county)
        with open(data_county, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([county[x] for x in fields])






    # fields = ['COUNTY', 'COUNTYNAME', 'PUIsTotal', 'Age_0_4', 'Age_5_14', 'Age_15_24', 'Age_25_34', 'Age_35_44', 'Age_45_54', 'Age_55_64', 'Age_65_74', 'Age_75_84', 'Age_85plus', 'Age_Unkn', 'PUIAgeRange', 'PUIAgeMedian', 'PUIFemale', 'PUIMale', 'PUISexUnkn', 'PUIFLRes', 'PUINotFLRes', 'PUIFLResOut', 'PUIContNo', 'PUIContUnkn', 'PUITravelNo', 'PUITravelYes', 'TPositive', 'TNegative', 'TInconc', 'TPending', 'T_Total_Res', 'C_Female', 'C_Male', 'C_SexUnkn', 'C_AllResTypes', 'C_Age_0_4', 'C_Age_5_14', 'C_Age_15_24', 'C_Age_25_34', 'C_Age_35_44', 'C_Age_45_54', 'C_Age_55_64', 'C_Age_65_74', 'C_Age_75_84', 'C_Age_85plus', 'C_Age_Unkn', 'C_AgeRange', 'C_AgeMedian', 'C_RaceWhite', 'C_RaceBlack', 'C_RaceOther', 'C_RaceUnknown', 'C_HispanicYES', 'C_HispanicNO', 'C_HispanicUnk', 'C_EDYes_Res', 'C_EDYes_NonRes', 'C_HospYes_Res', 'C_HospYes_NonRes', 'C_NonResDeaths', 'C_FLResDeaths', 'CasesAll', 'C_Men', 'C_Women', 'C_FLRes', 'C_NotFLRes', 'C_FLResOut', 'T_NegRes', 'T_NegNotFLRes', 'T_total', 'T_negative', 'T_positive', 'Deaths', 'EverMon', 'MonNow', "Scrape_Time"]
    # res = []
    # for x in raw["features"]:
    #     x = x["attributes"]
    #     x["Scrape_Time"] = now
    #     res.append([x[y] for y in fields])


    # # Open file
    # exists = os.path.exists(data_name)
    # f = open(data_name, 'a')
    # writer = csv.writer(f)
    # if not exists:
    #     writer.writerow(["Currently Hospitalized","Currently on Ventilator", "Total Nursing Home Residents", "Fraction Male",
    #                      "Fraction Female", "Age [0-18]", "Age [19-64]", "Age [65+]", "pullTime"])

    # # Scrape data
    # now = datetime.now()
    


    # # Get gender distribution
    # male = float(list(list(soup(text="Gender")[0].parent.parent.children)[3])[0].split()[2].strip('%'))/100
    # female = float(list(list(soup(text="Gender")[0].parent.parent.children)[3])[2].split()[2].strip('%'))/100

    # # Get age distribution
    # age1 = int(list(list(soup(text="Age")[0].parent.parent.children)[3])[0].split()[1].replace(',', ''))
    # age2 = int(list(list(soup(text="Age")[0].parent.parent.children)[3])[2].split()[1].replace(',', ''))
    # age3 = int(list(list(soup(text="Age")[0].parent.parent.children)[3])[4].split()[1].replace(',', ''))

    # # Write row
    # writer.writerow([hosp, vent, nurs, male, female, age1, age2, age3, now])

    # # Close file
    # f.close()

if __name__ == '__main__':
    run_AR({})
