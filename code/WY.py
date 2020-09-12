# https://public.tableau.com/profile/melissa.taylor#!/vizhome/EpiCOVIDtest/Dashboard

import base64
import csv
from datetime import datetime
from io import BytesIO
from johnutil.imgutil import getGraph, getCanvas, getColors
import os
from PIL import Image
import re
import requests
from selenium import webdriver
import sys
import time

def run_WY(args):
    # Parameters
    raw_name = '../WY/raw'
    data_name = '../WY/data/data.csv'
    now = str(datetime.now())

    # driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get("https://public.tableau.com/profile/melissa.taylor#!/vizhome/EpiCOVIDtest/Dashboard")
    time.sleep(10)  # More robust to wait for elements to appear...

    frames = driver.find_elements_by_tag_name('iframe')
    if len(frames) != 1:
        raise Exception("Could not find iframe")
    driver.switch_to.frame(frames[0])

    out = {}

    cases = getCanvas(driver.find_element_by_xpath('//*[@id="view3855800012607193825_5172391045180469540"]/div[1]/div[2]/canvas[1]'), driver).replace(",", "").replace("/", "")
    reCases = re.compile(r"(\d+)\s+lab\s+confirmed\s+cases\s+(\d+)\s+recovered")
    match = reCases.match(cases.strip().lower())
    if match:
        out["TotalConfirmedCases"] = match.group(1)
        out["RecoveredConfirmedCases"] = match.group(2)
    else:
        raise Exception("Warning: no total cases extracted for Wyoming; got string" + cases)

    pcases = getCanvas(driver.find_element_by_xpath('//*[@id="view3855800012607193825_2191712128240212356"]/div[1]/div[2]/canvas[1]'), driver).replace(",", "").replace("/", "")
    rePCases = re.compile(r"(\d+)\s+probable\s+cases\s+(\d+)\s+recovered")
    match = rePCases.match(pcases.strip().lower())
    if match:
        out["TotalProbableCases"] = match.group(1)
        out["RecoveredProbableCases"] = match.group(2)
    else:
        raise Exception("Warning: no total cases extracted for Wyoming; got string" + cases)
        
    deaths = getCanvas(driver.find_element_by_xpath('//*[@id="view3855800012607193825_11972683903544902318"]/div[1]/div[2]/canvas[1]'), driver).replace(",", "").replace("/", "")
    reDeath = re.compile(r"(\d+)\s+death")
    match = reDeath.match(deaths.strip().lower())
    if match:
        out["Deaths"] = match.group(1)
    else:
        out["Deaths"] = None
        print("Warning: no death count for Wyoming; got string", deaths)

    ages = getGraph(driver.find_element_by_xpath('//*[@id="view3855800012607193825_719033729591027206"]/div[1]/div[2]/canvas[1]'), (78, 121, 167, 255), driver)
    if len(ages) != 8:
        raise Exception("Wrong age count for WY")
    for age, val in zip(["0_17", "18_29", "30_39", "40_49", "50_59", "60_69", "70_79", "80_plus"], ages):
        out["Pct_Age_" + age] = round(val, 1)

    genders = getGraph(driver.find_element_by_xpath('//*[@id="view3855800012607193825_14275175901841894353"]/div[1]/div[2]/canvas[1]'), (78, 121, 167, 255), driver)
    genderLabels = [x.title() for x in getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId32"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver).strip().split()]
    if len(genders) != 2 or len(genderLabels) != 2 or " ".join(sorted(genderLabels)) != "Female Male":
        raise Exception("Wrong gender vals for WY")
    for gender, val in zip(genderLabels, genders):
        out["Pct_Gender_" + gender] = round(val, 1)

    symptoms = getGraph(driver.find_element_by_xpath('//*[@id="view3855800012607193825_13010788587209822541"]/div[1]/div[2]/canvas[1]'), (78, 121, 167, 255), driver)
    symptomLabels = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId49"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver).strip()
    symptomLabels = [x.strip().title().replace(" ", "") for x in symptomLabels.split("\n") if x != ""]
    if len(symptoms) != 14 or len(symptomLabels) != 14 or " ".join(sorted(symptomLabels)) != 'AbdominalPain Chills Cough Diarrhea Fatigue Fever Headache LossOfSmell/Taste MuscleAches NauseaOrVomiting None RunnyNose ShortnessOfBreath SoreThroat':
        print(sorted(symptomLabels))
        raise Exception("Unexpected symptoms in WY")
    for symptom, val in zip(symptomLabels, symptoms):
        out["Pct_Symptom_" + symptom] = round(val, 1)

    exposures = getGraph(driver.find_element_by_xpath('//*[@id="view3855800012607193825_11422738650703355835"]/div[1]/div[2]/canvas[1]'), (78, 121, 167, 255), driver)
    exposureLabels = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId52"]/div/div/div/div/div[5]/div[1]/canvas'), driver).strip()
    exposureLabels = [x.strip().title().replace(" ", "").replace("CommunitySpread", "CommunityAcquired") for x in exposureLabels.split("\n") if x != ""]
    expected = 'CommunalLiving CommunityAcquired ContactWithAKnownCase DomesticTravel InternationalTravel Other PendingInvestigation Unknown'
    if len(exposures) != 8 or len(exposureLabels) != 8 or " ".join(sorted(exposureLabels)) != expected:
        print(" ".join(sorted(exposureLabels)))
        print(expected)
        raise Exception("Unexpected exposures in WY")
    for exposure, val in zip(exposureLabels, exposures):
        out["Pct_Exposure_" + exposure] = round(val, 1)

    underlying = getGraph(driver.find_element_by_xpath('//*[@id="view3855800012607193825_1672645675164053982"]/div[1]/div[2]/canvas[1]'), (78, 121, 167, 255), driver)
    underlyingLabels = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId53"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver).strip()
    underlyingLabels = [x.strip().title().replace(" ", "") for x in underlyingLabels.split("\n") if x != ""]
    if len(underlyingLabels) != 3 or len(underlying) != 3 or " ".join(sorted(underlyingLabels)) != "No Unknown Yes":
        raise Exception("Unexpected underlying conditions in WY")
    for ul, val in zip(underlyingLabels, underlying):
        out["Pct_UnderlyingCond_" + ul] = round(val, 1)

    hosp = getGraph(driver.find_element_by_xpath('//*[@id="view3855800012607193825_16872468006943659536"]/div[1]/div[2]/canvas[1]'), (78, 121, 167, 255), driver)
    hospLabels = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId54"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver).strip()
    hospLabels = [x.strip().title().replace(" ", "").replace("NoHospitalization", "No").replace("Hospitalization", "Yes") for x in hospLabels.split("\n") if x != ""]
    if len(hospLabels) != 3 or len(hosp) != 3 or " ".join(sorted(hospLabels)) != "No Unknown Yes":
        raise Exception("Unexpected hospitalization data in WY")
    for hh, val in zip(hospLabels, hosp):
        out["Pct_Hospitalized_" + hh] = round(val, 1)

    race = getGraph(driver.find_element_by_xpath('//*[@id="view3855800012607193825_4426486129312330342"]/div[1]/div[2]/canvas[1]'), (78, 121, 167, 255), driver)
    raceLabels = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId60"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver).strip()
    raceLabels = [x.strip().title().replace(" ", "") for x in raceLabels.split("\n") if x != ""]
    for idx in range(len(raceLabels)):
        if raceLabels[idx].find("Hawaii") >= 0:
            raceLabels[idx] = "PacificIslander"
    if len(race) != len(raceLabels) or sorted(raceLabels) != ['AmericanIndian', 'Asian', 'Black', 'Hispanic', 'Other', 'PacificIslander', 'Unknown', 'White']:
        raise Exception("Unexpected race data in WY")
    for rr, val in zip(raceLabels, race):
        out["Pct_Race_" + rr] = round(val, 1)

    driver.get("https://public.tableau.com/profile/melissa.taylor#!/vizhome/shared/8BBTPD39D")
    # driver.get("https://public.tableau.com/profile/melissa.taylor#!/vizhome/WyomingCOVID-19TestingDataDashboard/Dashboard1")
    # https://health.wyo.gov/publichealth/infectious-disease-epidemiology-unit/disease/novel-coronavirus/covid-19-testing-data/
    time.sleep(10)  # More robust to wait for elements to appear...
    frames = driver.find_elements_by_tag_name('iframe')
    if len(frames) != 1:
        raise Exception("Could not find iframe on second page")
    driver.switch_to.frame(frames[0])

    testing = getCanvas(driver.find_element_by_xpath('//*[@id="view4597669659173455094_6899958757650081769"]/div[1]/div[2]/canvas[1]'), driver).replace(",", "")
    testingLabels = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId10"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver)
    testingLabels = [x.strip().title().replace(" ", "").replace("_", "-") for x in testingLabels.split("\n") if x != ""]
    if sorted(testingLabels) != ['GrandTotal', 'Non-Wphl', 'Wphl']:
        print(testingLabels)
        raise Exception("Unexpected testing lab labels in WY")
    reTesting = re.compile(r"(\d+)\s+(\d+)\s+(\d+)")
    match = reTesting.match(testing.strip())
    if match:
        out["WPHLTotalTest"] = match.group(testingLabels.index("Wphl")+1)
        out["CommercialLabTotalTest"] = match.group(testingLabels.index("Non-Wphl")+1)
    else:
        print(testing.strip())
        print("Warning: unexpected testing lab results in WY; skipping extraction")
        out["WPHLTotalTest"] = None
        out["CommercialLabTotalTest"] = None

    # Find width of the testing positive region within the whole image
    testPos = driver.find_element_by_xpath('//*[@id="view4597669659173455094_10103530389136289716"]/div[1]/div[2]/canvas[1]')
    b64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", testPos)
    img = Image.open(BytesIO(base64.b64decode(b64)))
    pix = img.load()
    cols, rows = img.size  # indexing is backward...
    maxCol = None
    for c in range(cols):
        for r in range(rows):
            if pix[c,r] == (252, 141, 98, 255):
                maxCol = c
                continue
    if maxCol is None:
        print(getColors(testPos, driver))
        raise Exception("Could not find testing positive color in WY")
    out["TestPositivePercentage"] = (maxCol+1)/cols * 100

    testByAge = getGraph(driver.find_element_by_xpath('//*[@id="view4597669659173455094_719033729591027206"]/div[1]/div[2]/canvas[1]'), (191, 198, 212, 255), driver)
    ageLabels = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId12"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver)
    ageLabels = [x.strip().title().replace(" ", "") for x in ageLabels.split("\n") if x != ""]
    ageMap = {'<18Years': "0_18", '19-29Years': "19_29", '30-39Years': "30_39", '40-49Years': "40_49",
              '50-59Years': "50_59", '60-69Years': "60_69", '70-79Years': "70_79", '80+Years': "80_plus"}
    if len(ageLabels) != 8 or len(testByAge) != 8 or not all(x in ageMap for x in ageLabels):
        raise Exception("Unexpected test age layout")
    for dat, lab in zip(testByAge, ageLabels):
        out["Test_Pct_Age_" + ageMap[lab]] = dat

    driver.close()
        
    out["Scrape_Time"] = now
    fields = sorted([x for x in out])
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])

    # Let's make a best effort to get the raw data...
    img = requests.get("https://public.tableau.com/static/images/Ep/EpiCOVIDtest/Dashboard/1.png")
    with open("%s/%s.png" % (raw_name, now), "wb") as fp:
        fp.write(img.content)

    img = requests.get("https://public.tableau.com/static/images/Wy/WyomingCOVID-19TestingDataDashboard/Dashboard1/1.png")
    with open("%s/testing_%s.png" % (raw_name, now), "wb") as fp:
        fp.write(img.content)

    # csvdat = requests.get("https://public.tableau.com/vizql/w/WyomingCOVID-19TestingDataDashboard/v/Dashboard1/vud/sessions/E5320C76C83B4DACA26214E6C5E19004-0:0/views/4597669659173455094_8782631838366857802?csv=true")
    # with open("%s/testTS_%s.csv" % (raw_name, now), "w") as fp:
    #     fp.write(csvdat.text.replace("\t", ","))

if __name__ == '__main__':
    run_WY({})
