# https://public.tableau.com/profile/idaho.division.of.public.health#!/vizhome/DPHIdahoCOVID-19Dashboard_V2/Story1

import base64
import csv
from datetime import datetime
import io
from io import BytesIO
from johnutil.imgutil import getGraph, getCanvas, getColors, getStackedGraph
import os
from PIL import Image
import pandas as pd
import re
import requests
from selenium import webdriver
import sys
import time

def run_ID(args):
    # Parameters
    raw_name = '../ID/raw'
    data_name = '../ID/data/data.csv'
    now = str(datetime.now())

    out = {}

    # driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get("https://public.tableau.com/profile/idaho.division.of.public.health#!/vizhome/DPHIdahoCOVID-19Dashboard_V2/Story1")
    time.sleep(10)  # More robust to wait for elements to appear...
    driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="ng-app"]/body/div[1]/div[2]/section/div/div[2]/section[2]/figure/js-api-viz/div/iframe'))

    # out["TotalTested"] = None  # Removed this one

    # OCR scan text info
    texts = [("TotalCases", r"(\d+)\s+\(\d+\s+new\)\s+statewide\s+cases", '//*[@id="view11831741491762752444_11141899506553115835"]/div[1]/div[2]/canvas[1]', False),
             ("TotalHospitalizations", r"(\d+)\s+cases hospitalized", '//*[@id="view11831741491762752444_14784563920108749745"]/div[1]/div[2]/canvas[1]', True),
             ("ICUAdmissions", r"(\d+)\s+cases admitted to icu", '//*[@id="view11831741491762752444_8851338240052320464"]/div[1]/div[2]/canvas[1]', True),
             ("CasesAmongHCW", r"(\d+)\s+cases among health care workers", '//*[@id="view11831741491762752444_378066509776727316"]/div[1]/div[2]/canvas[1]', False),
             ("CasesRecovered", r"(\d+)\s+cases estimated recovered",'//*[@id="view11831741491762752444_15348675858672874598"]/div[1]/div[2]/canvas[1]', True)]
             # ("TotalDeaths", r"(\d+)", '//*[@id="view2142284533943777519_7098283575370063084"]/div[1]/div[2]/canvas[1]', False)

    texts.append(("TotalDeaths", r"total deaths:+\s*(\d+)\s*\(\s*\d+\s*confirmed\s+\d+\s+probable\)\s+rate per 100000 population:+\s+(\S+)\s*", '//*[@id="view13810090252421852225_17430862024409208946"]/div[1]/div[2]/canvas[1]', False))
    
    # Click Demographics tab
    driver.find_element_by_xpath('//*[@id="tabZoneId4"]/div/div/div/span[2]/div/span/span/span[2]').click()
    time.sleep(10)

    for field, regex, xpath, flipBW in texts:
        if field == "TotalDeaths":
            # Click Deaths Tab
            driver.find_element_by_xpath('//*[@id="tabZoneId4"]/div/div/div/span[2]/div/span/span/span[7]').click()
            time.sleep(10)
        # print(field)
        text = getCanvas(driver.find_element_by_xpath(xpath), driver, flipBW).replace(",", "")
        rr = re.compile(regex)
        match = rr.search(text.strip().lower())
        if match:
            out[field] = match.group(1).strip()
        else:
            if field == "TotalDeaths":
                list_deaths = text.split()
                print(list_deaths)
                print(len(list_deaths))
                exit()
                if len(list_deaths) != 8:
                    raise Exception("Check Total Deaths")
                total_deaths = None
                death_rate_100k = None
                try:
                    total_deaths = int(list_deaths[2])
                except ValueError:
                    print("Total Deaths not Int - Check!")
                    raise
                try:
                    death_rate_100k = float(list_deaths[7])
                except ValueError:
                    print("Death Rate not Number - Check!")
                    raise
                out["TotalDeaths"] = total_deaths
                out["Death_Rate_Per_100000"] = death_rate_100k
            else:
                out[field] = None
                # print(field)
                raise Exception("Warning: No " + field + " extracted for Idaho; got string " + text)

    # Grab a few data points in the DOM
    # out["TestsStateLab"] = None  # No longer convenient to pull
    # out["TestsCommercialLab"] = None  # No longer convenient to pull


    # Click Demographics tab
    driver.find_element_by_xpath('//*[@id="tabZoneId4"]/div/div/div/span[2]/div/span/span/span[2]').click()
    time.sleep(10)

    # Grab graphs for demographics
    genders = getGraph(driver.find_element_by_xpath('//*[@id="view11831741491762752444_4953159310065112757"]/div[1]/div[2]/canvas[1]'), (78, 121, 167, 255), driver)
    genderLabels = [x.title() for x in getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId65"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver).strip().split()]
    if len(genders) != 2 or len(genderLabels) != 2 or " ".join(sorted(genderLabels)) != "Female Male":
        raise Exception("Wrong gender vals for ID")
    for gender, val in zip(genderLabels, genders):
        out["Pct_Gender_" + gender] = round(val, 1)

    ages = getGraph(driver.find_element_by_xpath('//*[@id="view11831741491762752444_7110063204799374782"]/div[1]/div[2]/canvas[1]'), (78, 121, 167, 255), driver)
    ageLabels = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId77"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver).strip().split()
    ageExpect = ["<18", "18-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-99", "100+"]
    if len(ages) != 10 or sorted(ageLabels) != sorted(ageExpect):
        raise Exception("Wrong age groups for ID")
    for age, val in zip(ageLabels, ages):
        out["Pct_Age_" + age.replace("-", "_").replace("<18", "0_17").replace("+", "_plus")] = round(val, 1)

    # raceCanvas = driver.find_element_by_xpath('//*[@id="view2142284533943777519_17257039996537996977"]/div[1]/div[2]/canvas[1]')
    # cols = getColors(raceCanvas, driver)
    # nonGray = sorted([x for x in cols if cols[x] > 100 and (x[0] != x[1] or x[0] != x[2])])
    # if nonGray != [(43, 92, 138, 255)]:
    #     raise Exception("Unexpected colors in race plot for ID: " + str(nonGray))
    # raceDat = getStackedGraph(raceCanvas, [(43, 92, 138, 255)], driver)
    # raceLabels = ["White"]
    # for dat, lab in zip(raceDat, raceLabels):
    #     out["Death_Pct_Race_" + lab] = round(dat, 1)
    # if not "Asian" in raceLabels:
    #     out["Death_Pct_Race_Asian"] = None

    # # Click Deaths Tab
    # driver.find_element_by_xpath('//*[@id="tabZoneId4"]/div/div/div/span[2]/div/span/span/span[6]').click()
    # time.sleep(10)
    
    # # Get Ethnicity Death Pct
    # ethCanvas = driver.find_element_by_xpath('//*[@id="view13810090252421852225_17815945649314726624"]/div[1]/div[2]/canvas[1]')
    # cols = getColors(ethCanvas, driver)
    # nonGray = sorted([x for x in cols if cols[x] > 100 and (x[0] != x[1] or x[0] != x[2])])
    # if nonGray != [(44, 89, 133, 255), (196, 216, 243, 255)]:
    #     raise Exception("Unexpected colors in ethnicity plot for ID: " + str(nonGray))
    # ethDat = getStackedGraph(ethCanvas, [(44, 89, 133, 255), (196, 216, 243, 255)], driver)
    # ethLabels = ["NotHispanic", "Hispanic"]
    # for dat, lab in zip(ethDat, ethLabels):
    #     out["Death_Pct_Eth_" + lab] = round(dat, 1)
    driver.close()
    
    # # Manually collect race and ethn data
    print("Please load https://public.tableau.com/profile/idaho.division.of.public.health#!/vizhome/DPHIdahoCOVID-19Dashboard_V2/Story1 and click on the COVID-19 Demographics Tab")

    # Cases
    goodRace = input("Are there exactly 7 races in the dashboard: White, Asian, Black, Other Race, Multiple Race, American Indian, Native Hawaiian? Are there exactly two ethnicities: Non-hispanic and hispanic? (Y/N) ").lower()
    if goodRace not in ["y", "n"]:
        raise Exception("Invalid input")
    if goodRace == "n":
        raise Exception("Invalid races and/or ethnicities")
    out["Case_Pct_Race_White"] = float(input("Case Pct White? "))
    out["Case_Pct_Race_Other"] = float(input("Case Pct Other? "))
    out["Case_Pct_Race_NativeHawaiian"] = float(input("Case Pct Native Hawaiian? "))
    out["Case_Pct_Race_MultipleRaces"] = float(input("Case Pct Multiple Races? "))
    out["Case_Pct_Race_Black"] = float(input("Case Pct Black? "))
    out["Case_Pct_Race_Asian"] = float(input("Case Pct Asian? "))
    out["Case_Pct_Race_AmericanIndian"] = float(input("Case Pct American Indian? "))
    out["Case_Pct_Ethn_NonHispanic"] = float(input("Case Pct Non-Hispanic? "))
    out["Case_Pct_Ethn_Hispanic"] = float(input("Case Pct Hispanic? "))

    # Death
    print("Now click on the COVID-19 Related Deaths Demographics Tab")
    goodRace = input("Are there exactly 6 races in the dashboard: White, Asian, Black, American Indian, Native Hawaiian and Other? Are there exactly 2 ethnicities: Non-hispanic and hispanic? (Y/N) ").lower()
    if goodRace not in ["y", "n"]:
        raise Exception("Invalid input")
    if goodRace == "n":
        raise Exception("Invalid races and/or ethnicities")
    out["Death_Pct_Race_White"] = float(input("Death Pct White? "))
    out["Death_Pct_Race_Other"] = float(input("Death Pct Other? "))
    out["Death_Pct_Race_NativeHawaiian"] = float(input("Death Pct Native Hawaiian? "))
    out["Death_Pct_Race_Black"] = float(input("Death Pct Black? "))
    out["Death_Pct_Race_Asian"] = float(input("Death Pct Asian? "))
    out["Death_Pct_Race_AmericanIndian"] = float(input("Death Pct American Indian? "))
    out["Death_Pct_Ethn_NonHispanic"] = float(input("Death Pct Non-Hispanic? "))
    out["Death_Pct_Ethn_Hispanic"] = float(input("Death Pct Hispanic? "))

    out["Scrape_Time"] = now
    fields = sorted([x for x in out])
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])

    # Let's make a best effort to get the raw data...
    img = requests.get("https://public.tableau.com/static/images/DP/DPHIdahoCOVID-19Dashboard_V2/Story1/1.png")
    with open("%s/%s.png" % (raw_name, now), "wb") as fp:
        fp.write(img.content)

if __name__ == '__main__':
    run_ID({})

