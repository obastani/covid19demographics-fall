from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import re
import sys
from urllib.request import urlopen
import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver import ActionChains
import json
import os

def run_AL(args):
    # Parameters
    raw_name = '../AL/raw'
    data_name = '../AL/data/data.csv'
    data_county = '../AL/data/data_county.csv'
    now = str(datetime.now())

    # Cases - Links
    c_age_link = ("c_age", "https://services7.arcgis.com/4RQmZZ0yaZkGR1zy/arcgis/rest/services/Statewide_COVID19_CONFIRMED_DEMOG_PUBLIC/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=AgeGroup&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22AgeGroup_Counts%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true")
    c_sex_link = ("c_sex","https://services7.arcgis.com/4RQmZZ0yaZkGR1zy/arcgis/rest/services/Statewide_COVID19_CONFIRMED_DEMOG_PUBLIC/FeatureServer/2/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Gender&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Gender_Counts%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true")
    c_race_link = ("c_race","https://services7.arcgis.com/4RQmZZ0yaZkGR1zy/arcgis/rest/services/Statewide_COVID19_CONFIRMED_DEMOG_PUBLIC/FeatureServer/3/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Racecat&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Race_Counts%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true")
    c_ethn_link = ("c_ethn","https://services7.arcgis.com/4RQmZZ0yaZkGR1zy/arcgis/rest/services/Statewide_COVID19_CONFIRMED_DEMOG_PUBLIC/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Ethnicity&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Ethnicity_Counts%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true")
    # Deaths - Links
    d_age_link = ("d_age","https://services7.arcgis.com/4RQmZZ0yaZkGR1zy/arcgis/rest/services/DIED_FROM_COVID19_STWD_DEMO_PUBLIC/FeatureServer/3/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=yearcats&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22DiedFromCovid19%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true")
    d_sex_link = ("d_sex","https://services7.arcgis.com/4RQmZZ0yaZkGR1zy/arcgis/rest/services/DIED_FROM_COVID19_STWD_DEMO_PUBLIC/FeatureServer/2/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Sex&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22DiedFromCovid19%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true")
    d_ethn_link = ("d_ethn","https://services7.arcgis.com/4RQmZZ0yaZkGR1zy/arcgis/rest/services/DIED_FROM_COVID19_STWD_DEMO_PUBLIC/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=EthnicityCat&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22DiedFromCovid19%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true")
    d_race_link = ("d_race","https://services7.arcgis.com/4RQmZZ0yaZkGR1zy/arcgis/rest/services/DIED_FROM_COVID19_STWD_DEMO_PUBLIC/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=Racecat&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22DiedFromCovid19%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&resultType=standard&cacheHint=true")
    # County - Links
    county_link = ("county","https://services7.arcgis.com/4RQmZZ0yaZkGR1zy/arcgis/rest/services/COV19_Public_Dashboard_ReadOnly/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=102100&resultOffset=0&resultRecordCount=70&resultType=standard&cacheHint=true")

    # List of links
    links = [c_age_link, c_sex_link, c_race_link, c_ethn_link, d_age_link, d_sex_link, d_ethn_link, d_race_link, county_link]

    # Expected fields
    exp_fields = {
        "c_age": ['>= 65', '0-4', '25-49', '50-64', '5-17', '18-24', 'Unknown'],
        "c_sex": ['Female', 'Male', 'Unknown'],
        "c_race": ['Asian', 'Black', 'Other', 'Unknown', 'White'],
        "c_ethn": ['Hispanic/Latino', 'Not Hispanic/Latino', 'Unknown'],
        "d_age": ['>= 65', '0-4', '25-49', '50-64', '5-17', '18-24', 'Unknown'],
        "d_sex": ['F', 'M', 'U'],
        "d_ethn": ['Hispanic/Latino', 'Not Hispanic/Latino', 'Unknown'],
        "d_race": ['Asian', 'Black', 'Other', 'Unknown', 'White']
    }
    # Expected Keys
    exp_keys = {
        "c_age": "AgeGroup",
        "c_sex": "Gender",
        "c_race": "Racecat",
        "c_ethn": "Ethnicity",
        "d_age": "yearcats",
        "d_sex": "Sex",
        "d_ethn": "EthnicityCat",
        "d_race": "Racecat"
    }
    out = {}
    out_county = []
    for cat, link in links:
        raw = requests.get(link).json()
        with open("%s/%s_%s.json" % (raw_name, now, cat), "w") as fp:
            json.dump(raw, fp)
        if "county" in cat:
            for county in raw["features"]:
                attributes = county["attributes"]
                county_val = {
                    "Scrape Time": now,
                    "County Name": attributes["CNTYNAME"],
                    "FIPS": attributes["CNTYFIPS"],
                    "Total Cases": attributes["CONFIRMED"],
                    "Total Deaths": attributes["DIED"],
                    "Total Tested": attributes["LabTestCount"]
                }
                out_county.append(county_val)
        else:
            for att in raw["features"]:
                category = att["attributes"][exp_keys[cat]]
                if category not in exp_fields[cat]:
                    raise Exception("Unexpected field for " + cat + ": " + category)
                val = att["attributes"]["value"]
                if "age" in cat:
                    if "c_" in cat:
                        out["# Cases Age [" + category + "]"] = val
                    else:
                        out["# Deaths Age [" + category + "]"] = val
                elif "sex" in cat:
                    if "c_" in cat:
                        if category == "Unknown":
                            out["Total Cases: " + category + " Sex"] = val
                        else:
                            out["Total Cases: " + category] = val
                    else:
                        if category == "F":
                            out["Total Deaths: Female"] = val
                        elif category == "U":
                            out["Total Deaths: Unknown Sex"] = val
                        else:
                            out["Total Deaths: Male"] = val
                elif "race" in cat:
                    if "c_" in cat:
                        if category == "Unknown" or category == "Other":
                            out["# Cases Race/Ethnicity: " + category + " Race"] = val
                        else:
                            out["# Cases Race/Ethnicity: " + category] = val
                    else:
                        if category == "Unknown" or category == "Other":
                            out["# Deaths Race/Ethnicity: " + category + " Race"] = val
                        else:
                            out["# Deaths Race/Ethnicity: " + category] = val
                elif "ethn" in cat:
                    if "c_" in cat:
                        if category == "Unknown":
                            out["# Cases Race/Ethnicity: " + category + " Ethnicity"] = val
                        else:
                            out["# Cases Race/Ethnicity: " + category] = val
                    else:
                        if category == "Unknown":
                            out["# Deaths Race/Ethnicity: " + category + " Ethnicity"] = val
                        else:
                            out["# Deaths Race/Ethnicity: " + category] = val
    out["Scrape Time"] = now
    
    # Output
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

if __name__ == '__main__':
    run_AL({})