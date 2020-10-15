# https://coronavirus.delaware.gov/ (scroll down)

import csv
from datetime import datetime
import json
import os
import requests
from urllib.request import urlopen, Request
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def run_DE(args):
    # Parameters
    raw_name = '../DE/raw'
    data_name = '../DE/data/data.csv'
    now = str(datetime.now())

    # Use Selenium to get Race + County data
    #driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get("https://myhealthycommunity.dhss.delaware.gov/locations/state#outcomes")
    time.sleep(5)
    
    statewide = {}

    # Accept Policy Use
    driver.find_element_by_xpath('//*[@id="accept"]').click()
    time.sleep(4)
    driver.find_element_by_xpath('/html/body/main/div/div/div[2]/section/form/button').click()
    time.sleep(4)
    
    # General Metrics
    total_cases = ((driver.find_element_by_xpath('//*[@id="cases-latest-status"]/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/span[1]').text).replace(",", "")).replace('*', '')
    confirmed_cases = (driver.find_element_by_xpath('//*[@id="cases-latest-status"]/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div[3]/div[2]/span').text).replace(",", "")
    probable_cases = (driver.find_element_by_xpath('//*[@id="cases-latest-status"]/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div[4]/div[2]/span').text).replace(",", "")

    element = driver.find_element_by_xpath('//*[@id="overview"]/div/article/div/div/div[2]/div[2]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/positive_cases_" + now + ".png")

    total_deaths = (driver.find_element_by_xpath('//*[@id="outcomes-trends"]/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div[1]/div/div[1]/div[1]').text).replace(",", "")

    element = driver.find_element_by_xpath('//*[@id="outcomes-trends"]/div/div/div[2]/div/div[2]/div/div[2]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/deaths_" + now + ".png")

    total_recovered = (driver.find_element_by_xpath('//*[@id="outcomes-trends"]/div/div/div[2]/div/div[1]/div/div[2]/div/div[1]/div[1]/div/div[1]/div[1]').text).replace(",", "")

    element = driver.find_element_by_xpath('//*[@id="outcomes-trends"]/div/div/div[2]/div/div[1]/div/div[2]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/recovered_" + now + ".png")

    total_negative = (driver.find_element_by_xpath('//*[@id="testing-trends"]/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div[1]/div/div[1]/div[1]').text).replace(",", "")

    element = driver.find_element_by_xpath('//*[@id="testing-trends"]/div/div/div[2]/div/div[1]/div/div[2]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/negative_cases_" + now + ".png")

    # total_tested = (driver.find_element_by_xpath('//*[@id="testing-trends"]/div/div/div[2]/div/div[1]/div/div[2]/div/div[1]/div[1]/div/div[1]/div[1]').text).replace(",", "")
    # hospitalized = (driver.find_element_by_xpath('//*[@id="overview"]/div/article/div/div/div[2]/div[1]/div[2]/div/div/div[2]/a/div[1]/div[1]/div/div[1]').text).replace(",", "")

    element = driver.find_element_by_xpath('//*[@id="overview"]/div/article/div/div/div[2]/div[1]/div[2]/div/div/div[3]/a/div[1]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/general_" + now + ".png")

    statewide["Total Cases"] = int(total_cases.strip('\n'))
    statewide["Confirmed Cases"] = int(confirmed_cases.strip('\n'))
    statewide["Probable Cases"] = int(probable_cases.strip('\n'))
    statewide["Total Deaths"] = int(total_deaths.split('\n')[0])
    statewide['Total Recovered'] = int(total_recovered.split('\n')[0])
    statewide["Total Negative"] = int(total_negative.split('\n')[0])
    # statewide["Total Tested"] = int(total_tested.split('\n')[0])
    # statewide["Total Hospitalized"] = int(hospitalized.strip('\n').replace("Hospitalized",""))
    statewide["Scrape_Time"] = now.strip('\n')

    # Click on count button
    driver.find_element_by_xpath('//*[@id="cases-demographics"]/div/div/div[1]/div/div/div/a[2]').click()
    time.sleep(2)
    # Age - Cases
    exp_ages = ["0-4", "5-17", "18-34", "35-49", "50-64", "65+"]
    tbl = driver.find_elements_by_xpath('//*[@id="total-cases-by-age"]/div[2]/div/table/tbody/*')
    element = driver.find_element_by_xpath('//*[@id="cases-demographics"]/div/div/div[2]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/age_cases_" + now + ".png")
    for row in tbl:
        # Get values
        vals = row.find_elements_by_xpath('.//*')
        str_vals = [x.text for x in vals]
        str_vals = [x.replace("\n\n", "") for x in str_vals]
        while("\n" in str_vals):
            str_vals.remove("\n")
        while("" in str_vals):
            str_vals.remove("")
        # Get race
        age = str_vals[0].strip()
        if age not in exp_ages:
            raise Exception("Unexpected age in cases: " + age)
        # Separating relative and absolute cases
        cases = (str_vals[3]).split(" ", 2)
        while("" in cases):
            cases.remove("")
        if len(cases) != 2:
            raise Exception("Unexpected value in cases for " + age )
        abs_case = (cases[0].replace(",", "")).strip("\n")
        pct_case = (((cases[1].replace("(","")).replace(")", "")).replace("%", "")).strip("\n")

        # Check we are getting the number values
        if str_vals[3] in exp_ages:
            raise Exception("Getting wrong value for cases: " + cases + " in " + age)
        
        # Add to statewide
        statewide["# Cases Age [" + age + "]"] = abs_case.strip('\n')
        statewide["% Cases Age [" + age + "]"] = pct_case.strip('\n')
    
    # Gender - Cases
    exp_gender = ["Female", "Male", "Unknown"]
    tbl = driver.find_elements_by_xpath('//*[@id="total-cases-by-sex"]/div[2]/div/table/tbody/*')
    element = driver.find_element_by_xpath('//*[@id="cases-demographics"]/div/div/div[2]/div[2]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/gender_cases_" + now + ".png")
    for row in tbl:
        # Get values
        vals = row.find_elements_by_xpath('.//*')
        str_vals = [x.text for x in vals]
        str_vals = [x.replace("\n\n", "") for x in str_vals]
        while("\n" in str_vals):
            str_vals.remove("\n")
        while("" in str_vals):
            str_vals.remove("")
        # Get race
        sex = str_vals[0].strip()
        if sex not in exp_gender:
            raise Exception("Unexpected race in cases: " + sex)
        # Separating relative and absolute cases
        cases = (str_vals[3]).split(" ", 2)
        while("" in cases):
            cases.remove("")
        if len(cases) != 2:
            raise Exception("Unexpected value in cases for " + sex)
        abs_case = cases[0].replace(",", "")
        pct_case = ((cases[1].replace("(","")).replace(")", "")).replace("%", "")

        # Check we are getting the number values
        if str_vals[3] in exp_gender:
            raise Exception("Getting wrong value for cases: " + cases + " in " + age)
        
        # Add to statewide
        if sex == "Unknown":
            statewide["Total Cases: " + sex + " Gender"] = abs_case.strip('\n')
            statewide["% Total Cases: " + sex + " Gender"] = pct_case.strip('\n')
        else:
            statewide["Total Cases: " + sex] = abs_case.strip('\n')
            statewide["% Total Cases: " + sex] = pct_case.strip('\n')
    
    # Age - Deaths
    exp_ages = ["0-4", "5-17", "18-34", "35-49", "50-64", "65+"]
    tbl = driver.find_elements_by_xpath('//*[@id="total-deaths-by-age"]/div[2]/div/table/tbody/*')
    element = driver.find_element_by_xpath('//*[@id="outcomes-demographics"]/div/div/div[2]/div[1]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/age_deaths_" + now + ".png")
    for row in tbl:
        # Get values
        vals = row.find_elements_by_xpath('.//*')
        str_vals = [x.text for x in vals]
        str_vals = [x.replace("\n\n", "") for x in str_vals]
        while("\n" in str_vals):
            str_vals.remove("\n")
        while("" in str_vals):
            str_vals.remove("")
        # Get race
        age = str_vals[0].strip()
        if age not in exp_ages:
            raise Exception("Unexpected race in deaths: " + age)
        # Separating relative and absolute deaths
        deaths = (str_vals[3]).split(" ", 2)
        while("" in deaths):
            deaths.remove("")
        if len(deaths) != 2:
            raise Exception("Unexpected value in deaths for " + age )
        abs_death = deaths[0].replace(",", "")
        pct_death = ((deaths[1].replace("(","")).replace(")", "")).replace("%", "")

        # Check we are getting the number values
        if str_vals[3] in exp_ages:
            raise Exception("Getting wrong value for deaths: " + deaths + " in " + age)
        
        # Add to statewide
        statewide["# Deaths Age [" + age + "]"] = abs_death.strip('\n')
        statewide["% Deaths Age [" + age + "]"] = pct_death.strip('\n')
    
    # Gender - Deaths
    exp_gender = ["Female", "Male"]
    tbl = driver.find_elements_by_xpath('//*[@id="total-deaths-by-sex"]/div[2]/div/table/tbody/*')
    element = driver.find_element_by_xpath('//*[@id="outcomes-demographics"]/div/div/div[2]/div[2]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/gender_deaths_" + now + ".png")
    for row in tbl:
        # Get values
        vals = row.find_elements_by_xpath('.//*')
        str_vals = [x.text for x in vals]
        str_vals = [x.replace("\n\n", "") for x in str_vals]
        while("\n" in str_vals):
            str_vals.remove("\n")
        while("" in str_vals):
            str_vals.remove("")
        # Get race
        sex = str_vals[0].strip()
        if sex not in exp_gender:
            raise Exception("Unexpected race in deaths: " + sex)
        # Separating relative and absolute deaths
        deaths = (str_vals[3]).split(" ", 2)
        while("" in deaths):
            deaths.remove("")
        if len(deaths) != 2:
            raise Exception("Unexpected value in deaths for " + sex)
        abs_death = deaths[0].replace(",", "")
        pct_death = ((deaths[1].replace("(","")).replace(")", "")).replace("%", "")

        # Check we are getting the number values
        if str_vals[3] in exp_gender:
            raise Exception("Getting wrong value for deaths: " + deaths + " in " + age)
        
        # Add to statewide
        if sex == "Unknown":
            statewide["Total Deaths: " + sex + " Gender"] = abs_death.strip('\n')
            statewide["% Total Deaths: " + sex + " Gender"] = pct_death.strip('\n')
        else:
            statewide["Total Deaths: " + sex] = abs_death.strip('\n')
            statewide["% Total Deaths: " + sex] = pct_death.strip('\n')

    # County - Positive Cases
    nc_county = (driver.find_element_by_xpath('//*[@id="overview"]/div/article/div/div/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]/a/div[2]/span[1]').text).replace(",", "")
    kent_county = (driver.find_element_by_xpath('//*[@id="overview"]/div/article/div/div/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/a/div[2]/span[1]').text).replace(",", "")
    ss_county = (driver.find_element_by_xpath('//*[@id="overview"]/div/article/div/div/div[2]/div[2]/div[2]/div/div/div[2]/div/div[3]/a/div[2]/span[1]').text).replace(",", "")

    statewide["New Castle County: Positive Cases"] = nc_county.strip('\n')
    statewide["Kent County: Positive Cases"] = kent_county.strip('\n')
    statewide["Sussex County: Positive Cases"] = ss_county.strip('\n')
    
    # Race - Cases
    exp_races = ["Non-Hispanic White", "Hispanic/Latino", "Non-Hispanic Black", "Another/Multiple", "Asian/Pacific Islander", "Unknown"]
    tbl = driver.find_elements_by_xpath('//*[@id="total-cases-by-race-ethnicity"]/div[2]/div/table/tbody/*')
    element = driver.find_element_by_xpath('//*[@id="total-cases-by-race-ethnicity"]/div[2]/div/table')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/race_cases_" + now + ".png")
    for row in tbl:
        # Get values
        vals = row.find_elements_by_xpath('.//*')
        str_vals = [x.text for x in vals]
        str_vals = [x.replace("\n\n", "") for x in str_vals]
        while("\n" in str_vals):
            str_vals.remove("\n")
        while("" in str_vals):
            str_vals.remove("")
        # Get race
        race = str_vals[0].strip()
        if race not in exp_races:
            raise Exception("Unexpected race in cases: " + race)
        # Separating relative and absolute cases
        cases = (str_vals[3]).split(" ", 2)
        while("" in cases):
            cases.remove("")
        if len(cases) != 2:
            raise Exception("Unexpected value in cases for " + race )
        abs_case = cases[0].replace(",", "")
        pct_case = ((cases[1].replace("(","")).replace(")", "")).replace("%", "")

        # Check we are getting the number values
        if str_vals[3] in exp_races:
            raise Exception("Getting wrong value for cases: " + cases + " in " + race)
        
        # Add to statewide
        statewide["# Cases Race/Ethnicity: " + race] = abs_case.strip('\n')
        statewide["% Cases Race/Ethnicity: " + race] = pct_case.strip('\n')

    # Race - Deaths
    exp_races = ["Non-Hispanic White", "Hispanic/Latino", "Non-Hispanic Black", "Another/Multiple", "Asian/Pacific Islander", "Unknown"]
    tbl = driver.find_elements_by_xpath('//*[@id="total-deaths-by-race-ethnicity"]/div[2]/div/table/tbody/*')
    element = driver.find_element_by_xpath('//*[@id="total-deaths-by-race-ethnicity"]/div[2]/div')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.save_screenshot(raw_name + "/race_deaths_" + now + ".png")
    for row in tbl:
        # Get values
        vals = row.find_elements_by_xpath('.//*')
        str_vals = [x.text for x in vals]
        str_vals = [x.replace("\n\n", "") for x in str_vals]
        while("\n" in str_vals):
            str_vals.remove("\n")
        while("" in str_vals):
            str_vals.remove("")
        # Get race
        race = str_vals[0].strip()
        if race not in exp_races:
            raise Exception("Unexpected race in deaths: " + race)
        # Separating relative and absolute cases
        deaths = (str_vals[3]).split(" ", 2)
        while("" in deaths):
            deaths.remove("")
        if len(cases) != 2:
            raise Exception("Unexpected value in deaths for " + race )
        abs_death = deaths[0].replace(",", "")
        pct_death = ((deaths[1].replace("(","")).replace(")", "")).replace("%", "")

        # Check we are getting the number values
        if str_vals[3] in exp_races:
            raise Exception("Getting wrong value for deaths: " + deaths + " in " + race)
        
        # Add to statewide
        statewide["# Deaths Race/Ethnicity: " + race] = abs_death.strip('\n')
        statewide["% Deaths Race/Ethnicity: " + race] = pct_death.strip('\n')


    fields = sorted([x for x in statewide])
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([statewide[x] for x in fields])

if __name__ == '__main__':
    run_DE({})
