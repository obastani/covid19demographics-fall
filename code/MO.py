# http://mophep.maps.arcgis.com/apps/MapSeries/index.html?appid=8e01a5d8d8bd4b4f85add006f9e14a9d
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys, os, pdb
from urllib.request import urlopen
import numpy as np
import pandas as pd
import requests 
import json

# def get_time(txt):
#     m = re.search("As of ([0-9]+:[0-9]+ [a,p]\.m\.) CT, ([A-Z][a-z]+ [0-9]+)", txt).groups()
#     time = m[0]
#     date = m[1]
#     return date, time

# stoi = lambda x: int(x.replace(",", ""))

# def read_table(t):
#     first = True
#     data = []
#     for x in t.find_all("tr"):
#         if first:
#             first = False
#             variables = [i.replace(" ", '_') for i in x.text.split("\n") if (len(i)>0 and not i.isspace()) ]
#         else:
#             tmp = [i for i in x.text.split("\n") if len(i)>0]
#             data.append([tmp[0]] + [stoi(i.replace("/td>", "")) for i in tmp[1:] if (len(i)>0 and not i.isspace()) ])
#     return data, variables


# def county_tables(t, df=None):
#     data, variables = read_table(t)
#     variables = ["stateAbbrev"] + variables
#     data = [["MO"] + i for i in data]
#     this_df = pd.DataFrame(data, columns=variables)
#     this_df.set_index("County", inplace=True)
#     if df is not None:
#         this_df = this_df.merge(df, on=["County", "stateAbbrev"], how="outer")
#     return this_df


# def already_scraped(scraped, date, time):
#     scraped_dt = [(i[2],i[3]) for i in scraped]
#     return (date, time) in scraped_dt


def run_MO(args):
    raw_name = "../MO/raw"
    data_name = "../MO/data/data.csv"
    county_data_name = "../MO/data/county_data.csv"
    now = datetime.now()

    # Out
    out = {}

    # Queries
    total_cases_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/lpha_boundry/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Cases%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
    total_deaths_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/lpha_boundry/FeatureServer/0/query?f=json&where=Deaths%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
    total_tests_pcr_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/Dashboard_Daily_Numbers_Automated/FeatureServer/0/query?f=json&where=Description%3D%27PCR%20Tested%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22value%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true'
    total_tests_ser_link = "https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/Dashboard_Daily_Numbers_Automated/FeatureServer/0/query?f=json&where=Description%3D%27SER%20Tested%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22value%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true"
    case_ethn_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/Cases_by_Ethnicity_Automated/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=3&resultType=standard&cacheHint=true'
    death_ethn_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/Death_by_Ethnicity_Automated/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=3&resultType=standard&cacheHint=true'
    case_race_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/Case_by_Race_Automated/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=20&resultType=standard&cacheHint=true'
    death_race_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/Death_by_Race_Automated/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=20&resultType=standard&cacheHint=true'
    case_age_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/lpha_boundry/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22under20%22%2C%22outStatisticFieldName%22%3A%22under20%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22twenty%22%2C%22outStatisticFieldName%22%3A%22twenty%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22twenty1%22%2C%22outStatisticFieldName%22%3A%22twenty1%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22thirty1%22%2C%22outStatisticFieldName%22%3A%22thirty1%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22thirty%22%2C%22outStatisticFieldName%22%3A%22thirty%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22fourty1%22%2C%22outStatisticFieldName%22%3A%22fourty1%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22fourty%22%2C%22outStatisticFieldName%22%3A%22fourty%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22fifty%22%2C%22outStatisticFieldName%22%3A%22fifty%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22fifty1%22%2C%22outStatisticFieldName%22%3A%22fifty1%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22sixty%22%2C%22outStatisticFieldName%22%3A%22sixty%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22sixty1%22%2C%22outStatisticFieldName%22%3A%22sixty1%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22seventy%22%2C%22outStatisticFieldName%22%3A%22seventy%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22seventy1%22%2C%22outStatisticFieldName%22%3A%22seventy1%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22eighty%22%2C%22outStatisticFieldName%22%3A%22eighty%22%7D%5D&resultType=standard&cacheHint=true'
    death_age_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/Death_by_Age_Automated/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=8&resultType=standard&cacheHint=true'
    case_gender_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/Dashboard_Daily_Numbers_Automated/FeatureServer/0/query?f=json&where=Board%3D%27Cases%20Demo%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=25&resultType=standard&cacheHint=true'
    county_link = 'https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/lpha_boundry/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=true&spatialRel=esriSpatialRelIntersects&maxAllowableOffset=2445&geometry=%7B%22xmin%22%3A-11271098.442820927%2C%22ymin%22%3A3757032.814276945%2C%22xmax%22%3A-10018754.17139693%2C%22ymax%22%3A5009377.085700942%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100&resultType=tile'

    # "https://services6.arcgis.com/Bd4MACzvEukoZ9mR/arcgis/rest/services/lpha_boundry/FeatureServer/0/query?where=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=under20%2C+twenty%2C+thirty%2C+fourty%2C+fifty%2C+sixty%2C+seventy%2C+eighty&returnGeometry=true&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=html&token="
    # Totals 
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
    # Total Deaths number
    total_deaths_raw = requests.get(total_deaths_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_total_deaths"), "w") as fp:
        json.dump(total_cases_raw, fp)
    # Process
    try:
        out["Total Deaths"] = total_deaths_raw["features"][0]["attributes"]["value"]
    except:
        print("Unexpected Total Deaths Value")
        raise 
    # Total Tests - Serology
    total_tests_ser_raw = requests.get(total_tests_ser_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_total_tests_ser"), "w") as fp:
        json.dump(total_tests_ser_raw, fp)
    # Process
    try:
        #print(total_tests_ser_raw["features"][0]["attributes"]["value"])
        out["Total Tested: Serology"] = total_tests_ser_raw["features"][0]["attributes"]["value"]
    except:
        print("Unexpected Total Tests Serology")
        raise 
    # Total Tests - PCR
    total_tests_pcr_raw = requests.get(total_tests_pcr_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_total_tests_pcr"), "w") as fp:
        json.dump(total_tests_pcr_raw, fp)
    # Process
    try:
        #print(total_tests_pcr_raw["features"][0]["attributes"]["value"])
        out["Total Tested: PCR"] = total_tests_pcr_raw["features"][0]["attributes"]["value"]
    except:
        print("Unexpected Total Tests PCR")
        raise
    # Ethnicity
    # Ethnicity Cases
    case_ethn_raw = requests.get(case_ethn_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_case_ethn"), "w") as fp:
        json.dump(case_ethn_raw, fp)
    # Process
    values = case_ethn_raw["features"]
    expected_fields = ["HISPANIC", "NON HISPANIC", "OTHER"]
    for ethn in values:
        attributes= ethn["attributes"]
        if attributes["ETHNICITY"] not in expected_fields:
            if attributes["ETHNICITY"] == "TOTAL":
                continue
            elif "NON HISPANIC" in attributes["ETHNICITY"]:
                continue
            else:
                raise Exception("Unexpected field in Ethnicity Cases: " + attributes["ETHNICITY"])
        eth_var = attributes["ETHNICITY"]
        if "NON HISPANIC" in attributes["ETHNICITY"]:
            eth_var = "NON HISPANIC"
        out["Total Cases: ethn_" + eth_var] = attributes["Frequency"]
        out["% Total Cases: ethn_" + eth_var] = attributes["Percent_"] * 100
    # Ethnicity Death
    death_ethn_raw = requests.get(death_ethn_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_death_ethn"), "w") as fp:
        json.dump(death_ethn_raw, fp)
    # Process
    values = death_ethn_raw["features"]
    expected_fields = ["HISPANIC", "NON HISPANIC", "OTHER"]
    for ethn in values:
        attributes= ethn["attributes"]
        #print(attributes)
        # print(attributes["ETHNICITY"])
        if attributes["ETHNICITY"] not in expected_fields:
            raise Exception("Unexpected field in Ethnicity Deaths: " + attributes["ETHNICITY"])
        out["Total Deaths: ethn_" + attributes["ETHNICITY"]] = attributes["Frequency"]
        if attributes["Percent_"]:
            out["% Total Deaths: ethn_" + attributes["ETHNICITY"]] = attributes["Percent_"] * 100
        else:
            out["% Total Deaths: ethn_" + attributes["ETHNICITY"]] = 0

    # Race
    # Case Race
    case_race_raw = requests.get(case_race_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_case_race"), "w") as fp:
        json.dump(case_race_raw, fp)
    # Process
    values = case_race_raw["features"]
    expected_fields = ["BLACK", "MULTI RACE", "Other Race", "REFUSED TO ANSWER RACE", "UNKNOWN RACE", "WHITE"]
    for race in values:
        attributes= race["attributes"]
        if attributes["RACE"] not in expected_fields:
            raise Exception("Unexpected field in Race Cases: " + attributes["RACE"]) 
        out["Total Cases: race_" + attributes["RACE"]] = attributes["Frequency"]
        out["% Total Cases: race_" + attributes["RACE"]] = attributes["Percent_"] * 100
    # Death Race
    death_race_raw = requests.get(death_race_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_death_race"), "w") as fp:
        json.dump(death_race_raw, fp)
    # Process
    values = death_race_raw["features"]
    expected_fields = ["BLACK", "MULTI RACE", "Other Race", "REFUSED TO ANSWER RACE", "UNKNOWN RACE", "WHITE"]
    for race in values:
        attributes= race["attributes"]
        if attributes["RACE"] not in expected_fields:
            raise Exception("Unexpected field in Race Deaths")
        out["Total Deaths: race_" + attributes["RACE"].capitalize()] = attributes["Frequency"]
        out["% Total Deaths: race_" + attributes["RACE"].capitalize()] = attributes["Percent_"] * 100
    # Age
    # Dictionary Mapping
    age_translation = {
        "under20": "[0-19]", 
        "twenty": "[20-24]", 
        "twenty1": "[25-29]", 
        "thirty": "[30-34]", 
        "thirty1": "[35-39]", 
        "fourty": "[40-44]", 
        "fourty1": "[45-49]", 
        "fifty": "[50-54]", 
        "fifty1": "[55-59]", 
        "sixty": "[60-64]", 
        "sixty1": "[65-69]", 
        "seventy": "[70-74]", 
        "seventy1": "[75-79]", 
        "eighty": "[80+]"
    }
    # Age Case
    case_age_raw = requests.get(case_age_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_case_age"), "w") as fp:
        json.dump(case_age_raw, fp)
    # Process
    values = case_age_raw["features"]
    if len(values) != 1:
        raise Exception("Unexpected data response for case age")
    expected_fields = ["under20", "twenty", "twenty1", "thirty", "thirty1", "fourty", "fourty1", "fifty", "fifty1", "sixty", "sixty1", "seventy", "seventy1", "eighty"]
    for age in values:
        attributes= age["attributes"]
        for age in attributes:
            if age not in expected_fields:
                raise Exception("Unexpected field in Age Cases")
            out["# Cases Age " + age_translation[age]] = attributes[age]
    # Age Death
    age_translation = {
        "under_20_": "[0-19]", 
        "twenty": "[20-29]", 
        "thirty": "[30-39]", 
        "fourty": "[40-49]", 
        "fifty": "[50-59]", 
        "sixty": "[60-69]", 
        "seventy": "[70-79]", 
        "eighty": "[80+]"
    }
    death_age_raw = requests.get(death_age_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_death_age"), "w") as fp:
        json.dump(death_age_raw, fp)
    # Process
    values = death_age_raw["features"]
    expected_fields = ["0-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80+"]
    if len(values) != len(expected_fields):
        raise Exception("Unexpected data response for death age")
    for el in values:
        attributes= el["attributes"]
        age = attributes["age"]
        death_count = attributes["count_"]
        if age not in expected_fields:
            raise Exception("Unexpected field in Age Deaths")
        out["# Deaths Age [" + age + "]"] = death_count
    # Gender Cases
    case_gender_raw = requests.get(case_gender_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_case_gender"), "w") as fp:
        json.dump(case_gender_raw, fp)
    values = case_gender_raw["features"]
    # print(values)
    if len(values)!= 3:
        raise Exception("Unexpected data response for gender cases")
    expected_fields = ["Male", "Female", "Unknown**"]
    count = 0
    for el in values:
        attribute = el['attributes']
        if attribute["Description"] not in expected_fields:
            continue
        if attribute["Description"] == "Unknown**":
            out["Total Cases: UnknownGender"] = attribute["value"]
        else:
            out["Total Cases: " + attribute["Description"]] = attribute["value"]
        count += 1
    if count != 3:
        raise Exception("Did not collect all desired genders")
    # County
    out_county = []
    county_raw = requests.get(county_link).json()
    with open("%s/%s_%s.json" % (raw_name, now, "_county"), "w") as fp:
        json.dump(county_raw, fp)
    
    values = county_raw["features"]
    
    for county in values:
        county_val = county["attributes"]
        try:
            county_data = {
                "County Name": county_val["NAME"],
                "Total Cases": county_val["Cases"],
                "Total Deaths": county_val["Deaths"],                
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
        exists = os.path.exists(county_data_name)
        with open(county_data_name, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([county[x] for x in fields])

    
    # age_data_name = "../MO/data/age_data.csv"
    # congregate_living = "../MO/data/congregate.txt"
    # exists = False
    # scraped = []
    
    # if os.path.exists(data_name):
    #     fp = open(data_name, "r")
    #     reader = csv.reader(fp, delimiter=",")
    #     for row in reader:
    #         scraped.append(row)
    # writer = csv.writer(open(data_name, 'a'))
    # if scraped:
    #     exists = True
    #     variables = scraped[0]
    # tz = "MO"

    
    # url = "https://health.mo.gov/living/healthcondiseases/communicable/novel-coronavirus/results.php"
    # url_record = url
    # html = urlopen(url).read()
    # soup = BeautifulSoup(html, "html.parser")

    # g = open('{}/{}.html'.format(raw_name, now), 'w')
    # g.write(str(soup))
    # g.close()

    # x = soup.find("span", class_="text-danger")
    # cases = stoi(re.search("Cases in Missouri: ([0-9,\,]+)", x.text).groups()[0])
    # x = x.find_next().find_next()
    # deaths = stoi(re.search("Total Deaths: ([0-9,\,]+)", x.text).groups()[0])
    # x = x.find_next().find_next().find_next()
    # x = x.find_next().find_next()
    # tested = stoi(re.search("Patients tested.*: [A-Z, a-z, ]*([0-9,\,]+)", x.text).groups()[0])
    # x = x.find_next("p")
    # date, time = get_time(x.text)
    # # by county table
    # x = soup.find("div", class_="table w-auto")
    # t = [i for i in x.children][1]
    # df = county_tables(t)
    # # Aggregate by age
    # x = x.find_next("div", class_="table w-auto") 
    # t = [i for i in x.children][1]
    # age_data, age_variables = read_table(t)
    # age_variables = ["Age"+i[0] for i in age_data]
    # age_data = [i[1] for i in age_data]
    # # race info
    # img_race = requests.get("https://health.mo.gov/living/healthcondiseases/communicable/novel-coronavirus/img/cases-by-race.jpg")
    # img_ethnicity = requests.get("https://health.mo.gov/living/healthcondiseases/communicable/novel-coronavirus/img/cases-by-ethnicity.jpg")
    # with open(f"{raw_name}/{now}_case_by_race.png", 'wb') as fp:
    #     fp.write(img_race.content)
    # with open(f"{raw_name}/{now}_case_by_ethnicity.png", 'wb') as fp:
    #     fp.write(img_ethnicity.content)
    # x = x.find_next("div", class_="table w-auto") 
    # x = x.find_next("td", class_="text-center").find_next("td", class_="text-center")  
    # txt = x.text.replace(" and ","").split(",")
    # outbreak_txt = [i.replace(" ", "").replace("St.", "St. ") for i in txt]
    # # Death by county
    # x = x.find_next("div", class_="table w-auto") 
    # t = [i for i in x.children][1]
    # df = county_tables(t, df)
    # # Death by age 
    # x = x.find_next("div", class_="table w-auto") 
    # t = [i for i in x.children][1]
    # age_data_d, age_variables_d = read_table(t)
    # age_variables_d = ["Age_fatality"+i[0] for i in age_data_d]
    # age_data_d = [i[1] for i in age_data_d]
    # # How they got it (No longer available)
    # #x = x.find_next("div", class_="table w-auto") 
    # #t = [i for i in x.children][1]
    # #how_data, how_variables = read_table(t)
    # #how_variables = [i[0].replace(" ", "_") for i in how_data]
    # #how_variables = ["Unknown" if i == "Under_Investigation" else i for i in how_variables]
    # #how_data = [i[1] for i in how_data]
    # how_data = [np.nan, np.nan, np.nan, np.nan]
    # how_variables = ["Travel", "Contact", "No_Known_Contact", "Unknown"]
    # # sex variable 
    # x = x.find_next("div", class_="table w-auto") 
    # t = [i for i in x.children][1]
    # sex_data, _ = read_table(t)
    # sex_variables = [f"{i[0]}_sex" for i in sex_data]
    # sex_data = [i[1] for i in sex_data]
    # # death by ethnicity
    # img_race = requests.get("https://health.mo.gov/living/healthcondiseases/communicable/novel-coronavirus/img/deaths-by-race.jpg")
    # img_ethnicity = requests.get("https://health.mo.gov/living/healthcondiseases/communicable/novel-coronavirus/img/deaths-by-ethnicity.jpg")
    # with open(f"{raw_name}/{now}_death_by_race.png", 'wb') as fp:
    #     fp.write(img_race.content)
    # with open(f"{raw_name}/{now}_death_by_ethnicity.png", 'wb') as fp:
    #     fp.write(img_ethnicity.content)
    # pdf = requests.get("https://health.mo.gov/living/healthcondiseases/communicable/novel-coronavirus/pdf/gov-dashboard.pdf")
    # with open(f"{raw_name}/{now}_situation.pdf", 'wb') as fp:
    #     fp.write(pdf.content)

    # # Detailed age data 
    # url = "https://health.mo.gov/living/healthcondiseases/communicable/novel-coronavirus/cases-by-age.php"
    # html = urlopen(url).read()
    # soup = BeautifulSoup(html, "html.parser")
    # x = soup.find("table", class_="table col-xs-12 col-md-12 col-sm-12")
    # t = read_table(x)
    # age_df = pd.DataFrame(columns=t[1], data=t[0])
    # age_df["date"] = date
    # x = soup.find("table", class_="table col-xs-12 col-md-12 col-sm-12")
    # g = open(f"{raw_name}/Age_{now}.html", 'w')
    # g.write(str(soup))
    # g.close()
    
    # columns = ["state", "stateAbbrev", "date", "time", "cases", "deaths",
    #         "tested"] + age_variables + how_variables + sex_variables + ["link", "pullTime"] + age_variables_d
    # if exists: 
    #     if columns != variables:
    #         print(f"Old variables: {variables}\nNew variables: {columns}")
    #         raise ValueError
    # #writer.writerow(columns)
    # if not already_scraped(scraped, date, time): # should be done earlier but w/e 
    #     writer.writerow(["Missouri", "MO", date, time, cases, deaths, 
    #         tested] + age_data + how_data + sex_data + [url_record] + [now] + age_data_d)
    #     df["pullTime"] = now
    #     df.to_csv(county_data_name, mode="a", header=(not exists))
    #     age_df.to_csv(age_data_name, mode="a", header=(not exists))
    #     wri = csv.writer(open(congregate_living, 'a'))
    #     writer.writerow([date, time] + outbreak_txt)
        

    # #for row in scraped[1:]:
    # #    writer.writerow(row)

if __name__=="__main__":
    run_MO({})
    
