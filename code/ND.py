# https://www.health.nd.gov/diseases-conditions/coronavirus/north-dakota-coronavirus-cases

import csv
from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

def get_age(out, driver, cat, now, raw_name):
    # Right Click
    chart_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[67]/transform/div/div[3]/div')
    driver.execute_script("arguments[0].scrollIntoView();", chart_div)
    actionChains = ActionChains(driver)
    actionChains.context_click(chart_div).pause(3).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    # Scrape
    age_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[67]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[3]/div/*')
    val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[67]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div/*')
    if len(age_div) != len(val_div):
        raise Exception('Uneven values and ages')
    expected_ages = ['0-5', '6-11', '12-14', '15-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
    for age, case in zip(age_div, val_div):
        if age.text not in expected_ages:
            raise Exception("Unexpected age group")
        out[cat + age.text + "]"] = case.text
    # Raw
    driver.save_screenshot(raw_name + "/age_" + cat + "_" + now + ".png")
    # Return to original page
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[67]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)
    # Return
    return out

def get_gender_sp_race(out, driver, cat, now, raw_name):
    # Gender
    # Right Click
    chart_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[35]/transform/div/div[3]/div')
    driver.execute_script("arguments[0].scrollIntoView();", chart_div)
    actionChains = ActionChains(driver)
    actionChains.context_click(chart_div).pause(3).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    cat_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[35]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[3]/div/*')
    val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[35]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div/*')
    expected_cats = ["Female", "Male"]
    for ct, val in zip(cat_div, val_div):
        if ct.text not in expected_cats:
            raise Exception("Unexpected Gender: " + ct.text)
        out[cat + ": " + ct.text] = val.text
    # Raw
    driver.save_screenshot(raw_name + "/gender_" + cat + "_" + now + ".png")
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[35]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)
    # Spreadtype
    # Right Click
    chart_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[33]/transform/div/div[3]/div')
    driver.execute_script("arguments[0].scrollIntoView();", chart_div)
    actionChains = ActionChains(driver)
    actionChains.context_click(chart_div).pause(3).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    cat_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[33]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[3]/div/*')
    val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[33]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div/*')
    expected_cats = ["Community", "Close Contact", "Unknown", "Household Contact", "Travel", "Under Investigation"]
    for ct, val in zip(cat_div, val_div):
        if ct.text not in expected_cats:
            raise Exception("Unexpected Spread Type: " + ct.text)
        out[cat + " Spread Type: " + ct.text] = val.text
    # Raw
    driver.save_screenshot(raw_name + "/spread_" + cat + "_" + now + ".png")
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[33]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)
    # Race
    # Right Click
    chart_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[68]/transform/div/div[3]/div/visual-modern/div')
    driver.execute_script("arguments[0].scrollIntoView();", chart_div)
    actionChains = ActionChains(driver)
    actionChains.context_click(chart_div).pause(3).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    cat_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[68]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[3]/div/*')
    val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[68]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div/*')
    expected_cats = ["White", "Unknown", "American Indian", "2 or More", "Asian", "Other", "Black"]
    for ct, val in zip(cat_div, val_div):
        if ct.text not in expected_cats:
            raise Exception("Unexpected Race: " + ct.text)
        out[cat + " Race: " + ct.text] = val.text
    # Raw
    driver.save_screenshot(raw_name + "/race_" + cat + "_" + now + ".png")
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[68]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)
    
    return out

def get_age_hosp(out, driver, now, cat, raw_name):
    # Raw
    driver.save_screenshot(raw_name + "/hosp_age_" + cat + "_" + now + ".png")
    age_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[23]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[3]/div/*')
    val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[23]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div/*')
    if len(age_div) != len(val_div):
        raise Exception('Uneven values and ages')
    expected_ages = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
    for age, hosp in zip(age_div, val_div):
        if age.text not in expected_ages:
            raise Exception("Unexpected age group")
        expected_ages.append(age.text)
        out[cat + age.text + "]"] = hosp.text
    # Return
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[23]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)
    return out

def get_age_death(out, driver, now, cat, raw_name):
    # Raw
    driver.save_screenshot(raw_name + "/death_age_" + cat + "_" + now + ".png")
    age_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[22]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[3]/div/*')
    val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[22]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div/*')
    if len(age_div) != len(val_div):
        raise Exception('Uneven values and ages')
    expected_ages = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
    for age, death in zip(age_div, val_div):
        if age.text not in expected_ages:
            raise Exception("Unexpected age group")
        out[cat + age.text + "]"] = death.text
    # Return
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[22]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)
    return out

def run_ND(args):
    # Parameters
    raw_name = '../ND/raw'
    data_name = '../ND/data/data.csv'
    now = str(datetime.now())

    r = requests.get("https://www.health.nd.gov/diseases-conditions/coronavirus/north-dakota-coronavirus-cases").text
    soup = BeautifulSoup(r, "html.parser")
    url = soup.find('iframe')["src"]

    # Using Selenium
    # driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get(url)
    time.sleep(10)
    out = {}
    # Change focus
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[51]/transform/div/div[3]/div/visual-modern').click()
    # Collect raw
    driver.save_screenshot(raw_name + "/overview_" + now + ".png")
    # New Tests, New Positive, Cum Tests, Cum Positive, Active Positives, % Population Tested
    out["Active Positive Cases"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[50]').text).replace(',','').split('\n')[1])
    out["New Tests: Total Processed"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[64]').text).replace(',','').split('\n')[1])
    out["New Tests: First Time Tested"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[135]').text).replace(',','').split('\n')[1])
    out["New Positives: Total"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[75]').text).replace(',','').split('\n')[1])
    out["New Positives: Tested Negative before Positive"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[66]').text).replace(',','').split('\n')[1])
    out["Total Tests"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[137]').text).replace(',','').split('\n')[1])
    out["Total Tested: Unique Individuals"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[139]').text).replace(',','').split('\n')[1])
    out["Total Positive Cases"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[141]').text).replace(',','').split('\n')[1])
    out["Total Positive Cases: Tested Negative before Positive"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[142]').text).replace(',','').split('\n')[1])
    out["Total Deaths"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[60]').text).replace(',','').split('\n')[1])
    out["Total Recovered"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[145]').text).replace(',','').split('\n')[1])
    # Age for Actives, Age for Positives
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[42]/transform/div/div[3]/div/visual-modern/div/button').click()
    time.sleep(7)
    out = get_age(out, driver, '# Positive Cases Age [', now, raw_name)
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[41]/transform/div/div[3]/div/visual-modern/div/button').click()
    time.sleep(7)
    out = get_age(out, driver, '# Active Cases Age [', now, raw_name)
    # Gender, Spreadtype, Race (Active and Cum Positives)
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[36]/transform/div/div[3]/div/visual-modern/div/button').click()
    time.sleep(7)
    out = get_gender_sp_race(out, driver, "Total Positive", now, raw_name)
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[34]/transform/div/div[3]/div/visual-modern/div/button').click()
    time.sleep(7)
    out = get_gender_sp_race(out, driver, "Total Active", now, raw_name)

    # Hospitalizations 
    chart_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[27]/transform/div/div[3]/div/visual-modern')
    driver.execute_script("arguments[0].scrollIntoView();", chart_div)
    # Raw
    driver.save_screenshot(raw_name + "/hosp_death_" + now + ".png")
    out["COVID Active Non-ICU"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[14]').text).replace(',','').split('\n')[2])
    out["COVID Total Non-ICU"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[13]').text).replace(',','').split('\n')[2])
    out["COVID Active ICU"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[17]').text).replace(',','').split('\n')[1])
    out["COVID Total ICU"] = int((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[15]').text).replace(',','').split('\n')[1])
    out["% Non-ICU occupied due to COVID"] = float((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[24]').text).replace('%','').split('\n')[1])
    out["% ICU occupied due to COVID"] = float((driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[25]').text).replace('%','').split('\n')[1])
    # Deaths by Age, Hospitalization by age
    # Hosp
    # Right Click
    chart_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[23]/transform/div/div[3]/div')
    driver.execute_script("arguments[0].scrollIntoView();", chart_div)
    actionChains = ActionChains(driver)
    actionChains.context_click(chart_div).pause(3).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    out = get_age_hosp(out, driver, now, "# Hospitalized Age [", raw_name)
    # Death
    # Right Click
    chart_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[22]/transform/div/div[3]/div')
    driver.execute_script("arguments[0].scrollIntoView();", chart_div)
    actionChains = ActionChains(driver)
    actionChains.context_click(chart_div).pause(3).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    out = get_age_death(out, driver, now, "# Deaths Age [", raw_name)

    out["Scrape_Time"] = str(datetime.now())
    fields = sorted([x for x in out])
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])


    #########################################################################

    # expected = " ".join(sorted(["PositiveCases", "Negative", "TotalUniqueIndividualsTested", "Recovered", "CurrentlyHospitalized", "TotalHospitalized", "Deaths"]))
    # for x in soup.find_all("div", class_="circle"):
    #     out[x.p.text.replace(" ", "")] = int(x.h2.text)
    # if " ".join(sorted([x for x in out])) != expected:
    #     raise Exception("Unexpected circles in ND")

    # dats = [x for x in soup.find_all("div", class_="paragraph__column")]

    # genderDiv = [x for x in dats if x.div.text == "Cases by Gender"]
    # if len(genderDiv) != 1:
    #     raise Exception("Unexpected gender structure in ND")
    # ginfo = json.loads(genderDiv[0].find("div", class_="charts-highchart")["data-chart"])
    # gcats = ginfo["xAxis"]["categories"]
    # if " ".join(sorted(gcats)) not in ["Female Male", "Female Male Unknown"]:
    #     raise Exception("Unexpected gender labels in ND")
    # gdat = ginfo["series"][0]["data"]
    # for cat, dat in zip(gcats, gdat):
    #     out["Num" + cat] = dat
    # if not "Unknown" in gcats:
    #     out["NumUnknown"] = None

    # ageDiv = [x for x in dats if x.div.text == "Cases by Age Group"]
    # if len(ageDiv) != 1:
    #     raise Exception("Unexpected age structure in ND")
    # ainfo = json.loads(ageDiv[0].find("div", class_="charts-highchart")["data-chart"])
    # acats = [x.replace("-", "_").replace("+", "_plus") for x in ainfo["xAxis"]["categories"]]
    # if " ".join(sorted(acats)) != "0_9 10_9 20_29 30_39 40_49 50_59 60_69 70_79 80_plus" and " ".join(sorted(acats)) != "0_9 10_19 20_29 30_39 40_49 50_59 60_69 70_79 80_plus":
    #     print(" ".join(sorted(acats)))
    #     raise Exception("Unexpected age labels in ND")
    # for x in ainfo["series"]:
    #     if x["name"] in ["Total_Cases", "Positive_Cases"]:
    #         x["name"] = "Total Cases"
    # if sorted([x["name"] for x in ainfo["series"]]) != ["Deaths", "Recovered", "Total Cases"]:
    #     print(sorted([x["name"] for x in ainfo["series"]]))
    #     raise Exception("Unexpected age series in ND")
    # for ss in ainfo["series"]:
    #     for cat, dat in zip(acats, ss["data"]):
    #         if cat == "10_9":
    #             cat = "10_19"
    #         out[ss["name"].replace(" ", "") + "_Age_" + cat] = dat

    # hospDiv = [x for x in dats if "Hospitalized by age group" in x.div.text]
    # if len(hospDiv) != 1:
    #     raise Exception("Unexpected hospitalization structure in ND")
    # hinfo = json.loads(hospDiv[0].find("div", class_="charts-highchart")["data-chart"])
    # hcats = [x.replace("-", "_").replace("+", "_plus") for x in hinfo["xAxis"]["categories"]]
    # # print(hcats)
    # # Sometimes the labels for 10-19 come wrong - Change here
    # if " ".join(sorted(hcats)) != "0_9 10_19 20_29 30_39 40_49 50_59 60_69 70_79 80_plus" and " ".join(sorted(hcats)) != "0_9 10_9 20_29 30_39 40_49 50_59 60_69 70_79 80_plus":
    #     raise Exception("Unexpected hosp age labels in ND")
    # if sorted([x["name"] for x in hinfo["series"]]) != ["No", "Yes"]:
    #     raise Exception("Unexpected hosp age series in ND")
    # ss = [x for x in hinfo["series"] if x["name"] == "Yes"][0]
    # for cat, dat in zip(hcats, ss["data"]):
    #     # This if is if 10_19 comes as 10_9
    #     if cat == "10_9":
    #         cat = "10-19"
    #     out["Hosp_Age_" + cat] = dat
            
    # sourceDiv = [x for x in dats if x.div.text == "Source of Exposure"]
    # if len(sourceDiv) != 1:
    #     raise Exception("Unexpected source structure in ND")
    # sinfo = json.loads(sourceDiv[0].find("div", class_="charts-highchart")["data-chart"])

    # def cleanCat(x):
    #     x = x.replace(" ", "")
    #     if x == "ConfirmedTravel":
    #         return "Travel"
    #     elif x == "Household":
    #         return "HouseholdContact"
    #     elif x == "Community":
    #         return "CommunitySpread"
    #     else:
    #         return x
        
    # scats = [cleanCat(x) for x in sinfo["xAxis"]["categories"]]
    
    # if " ".join(sorted(scats)) != "CloseContact CommunitySpread HouseholdContact PossibleTravel Travel UnderInvestigation":
    #     print(sorted(scats))
    #     raise Exception("Unexpected source labels in ND")
    # sdat = sinfo["series"][0]["data"]
    # for cat, dat in zip(scats, sdat):
    #     out["Source_" + cat] = dat

    # updateDiv = [x for x in dats if "Last updated" in x.div.text]
    # if len(updateDiv) != 1:
    #     raise Exception("Unexpected update structure in ND")
    # reUpdate = re.compile(r"Last updated: (\d+/\d+/\d+)")
    # match = reUpdate.search(updateDiv[0].div.text)
    # if not match:
    #     raise Exception("Missing update in ND")
    # out["LastUpdated"] = str(datetime.strptime(match.group(1), "%m/%d/%Y"))
    

if __name__ == '__main__':
    run_ND({})
