# https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9
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
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

def get_testing_results(driver):
    chart_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div')
    driver.execute_script("arguments[0].scrollIntoView();", chart_div)
    actionChains = ActionChains(driver)
    actionChains.context_click(chart_div).pause(3).send_keys(Keys.DOWN).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    # Show table
    # show_table = driver.find_element_by_xpath('/html/body/div[6]/drop-down-list/ng-transclude/ng-repeat/drop-down-list-item/ng-transclude/ng-switch/div')
    # show_table.click()
    # time.sleep(2)
    # Get data
    values_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/*')
    values = []
    for val in values_div:
        val_val = val.find_element_by_class_name('pivotTableCellWrap ')
        values.append(val_val.text)
    if len(values) != 2:
        raise Exception("Unexpected negative and positive tests results")

    return values[0], values[1]


    
def getinfo(current_lab, out, driver, raw_name, now):
    # Boxes division
    div_test_performed = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/div/visual-modern/div')
    div_hosp_conf = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[22]/transform/div/div[3]/div/visual-modern/div')
    div_hosp_sus = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[9]/transform/div/div[3]/div/visual-modern/div')
    div_confirmed_cases = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div')
    div_deaths = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[9]/transform/div/div[3]/div/visual-modern/div')
    div_icu = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[23]/transform/div/div[3]/div/visual-modern/div')
    # Category strings
    testPerformed = "TotalTests"
    confirmed_cases = "ConfirmedCases"
    deaths = "Deaths"
    conf_hosp = "ConfirmedHospitalized"
    sus_hosp = "SuspectedHospitalized"
    icu = "ICU"

    # General Information
    # count = 0
    # for el in div_test_performed.find_elements_by_xpath(".//*"):
    #     print(count, el.text)
    #     count+=1
    out[current_lab + testPerformed] = div_test_performed.find_elements_by_xpath(".//*")[4].text
    out[current_lab + confirmed_cases] = div_confirmed_cases.find_elements_by_xpath(".//*")[4].text
    out[current_lab + deaths] = div_deaths.find_elements_by_xpath(".//*")[4].text
    out[current_lab + conf_hosp] = div_hosp_conf.find_elements_by_xpath(".//*")[4].text
    out[current_lab + sus_hosp] = div_hosp_sus.find_elements_by_xpath(".//*")[4].text
    out[current_lab + icu] = div_icu.find_elements_by_xpath(".//*")[4].text

    # Get Screenshot
    driver.save_screenshot(raw_name + "/summary_" + now + ".png")

    # print(out[current_lab + testPerformed], out[current_lab + confirmed_cases], out[current_lab + deaths])
    # if current_lab == "":
    # else:
    #     positive, negative = get_testing_results(driver)
    #     out[current_lab + patientsNegative] = negative
    #     out[current_lab + patientsPositive] = positive
    #     driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    #     time.sleep(2)

    return out

def gotoOther(main, dropdown, driver):
    # Move to div
    main.click()
    time.sleep(1)
    # Go to other page 
    other_page = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/visual-container-header-modern/div/div[1]/div/visual-header-item-container/div')
    other_page.click()
    time.sleep(2)
    # Dropdown
    dropdown.click()
    time.sleep(2)

def goback(return_button):
    return_button.click()
    time.sleep(2)

def collect(current_lab, main, dropdown, xpath, out, driver):
    # Go to other page
    gotoOther(main, dropdown, driver)
    # If UMC, then unselect all:
    if current_lab == "Lab_UMC_":
        # Unselect all
        all_select = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[1]/div/span')
        all_select.click()
    # Select
    select = driver.find_element_by_xpath(xpath)
    select.click()
    # Go back
    return_button = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button')
    goback(return_button)
    # Add to Out
    return getinfo(current_lab, out, driver)
    
def get_age_gender_race(driver, out, cat):
    raw_name = '../NV/raw'
    now = str(datetime.now())

    # Get age
    age_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[1]')
    driver.execute_script("arguments[0].scrollIntoView();", age_div)
    actionChains = ActionChains(driver)
    actionChains.context_click(age_div).pause(3).send_keys(Keys.DOWN).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    # Get table
    headers_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/*')
    values_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/*')

    if len(headers_div) != len(values_div):
        raise Exception("Age data not right")

    if len(headers_div) == 0 or len(values_div) == 0:
        raise Exception("Empty tables")

    expected_ages = ["<10", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"]

    # Add to Out
    for header, val in zip (headers_div, values_div):
        header_val = header.find_element_by_class_name('pivotTableCellWrap ')
        val_val = val.find_element_by_class_name('pivotTableCellWrap ')
        head = (header_val.text).strip()
        if head not in expected_ages:
            raise Exception("Unexpected age headers")
        if str(head) == "<10":
            head = "0-9"
        elif str(head) == "70+":
            head = "70_plus"
        elif str(head) == "Not Reported":
            head = "Unknown"
        head = str(head).replace("-","_")
        out[cat + head] = val_val.text

    # Get Screenshot
    driver.save_screenshot(raw_name + "/age_" + cat + "_" + now + ".png")

    # Get Gender data 
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)
    gender_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[9]/transform/div/div[3]/div/visual-modern/div/div/div[1]')
    driver.execute_script("arguments[0].scrollIntoView();", gender_div)
    actionChains = ActionChains(driver)
    actionChains.context_click(gender_div).pause(3).send_keys(Keys.DOWN).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    # show_table = driver.find_element_by_xpath('/html/body/div[6]/drop-down-list/ng-transclude/ng-repeat/drop-down-list-item/ng-transclude/ng-switch/div')
    # show_table.click()
    # time.sleep(2)
    # Get table
    headers_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[9]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/*')
    values_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[9]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/*')

    if len(headers_div) != len(values_div):
        print(len(headers_div), len(values_div))
        raise Exception("Gender data not right")

    if len(headers_div) == 0 or len(values_div) == 0:
        raise Exception("Empty tables")

    expected_genders = ["Male", "Female"]
    count = 0
    # Add to Out
    for header, val in zip (headers_div, values_div):
        header_val = header.find_element_by_class_name('pivotTableCellWrap ')
        val_val = val.find_element_by_class_name('pivotTableCellWrap ')
        head = (header_val.text).strip()
        if head not in expected_genders:
            raise Exception("Unexpected Gender")
        if head == "Not Reported":
            head = "GenderUnknown"
        if head == "Unknown":
            head = "GenderUnknown"
        out[cat + head] = val_val.text
        count += 1
    if count != len(expected_genders):
        raise Exception("Unexpected number of genders")
    
    # Get Screenshot
    driver.save_screenshot(raw_name + "/gender_" + cat + "_" + now + ".png")

    # Get Race data 
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[9]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)
    race_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/div/visual-modern/div/div/div[1]')
    driver.execute_script("arguments[0].scrollIntoView();", race_div)
    actionChains = ActionChains(driver)
    actionChains.context_click(race_div).pause(3).send_keys(Keys.DOWN).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    # show_table = driver.find_element_by_xpath('/html/body/div[6]/drop-down-list/ng-transclude/ng-repeat/drop-down-list-item/ng-transclude/ng-switch/div')
    # show_table.click()
    # time.sleep(2)
    # Get table
    headers_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/*')
    values_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/*')

    if len(headers_div) != len(values_div):
        raise Exception("Race data not right")

    if len(headers_div) == 0 or len(values_div) == 0:
        raise Exception("Empty tables")

    expected_races = ["White", "Hispanic", "Black", "Asian", "AIAN", "Other"]
    # Add to Out
    for header, val in zip (headers_div, values_div):
        header_val = header.find_element_by_class_name('pivotTableCellWrap ')
        val_val = val.find_element_by_class_name('pivotTableCellWrap ')
        head = (header_val.text).strip()
        if head not in expected_races:
            raise Exception("Unexpected Race/Ethnicity")
        out[cat + head] = val_val.text
    
    # Get Screenshot
    driver.save_screenshot(raw_name + "/race_" + cat + "_" + now + ".png")

    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)
    return out
    
def run_NV(args):
    # Parameters
    raw_name = '../NV/raw'
    data_name = '../NV/data/data.csv'
    data_county = '../NV/data/data_county.csv'
    now = str(datetime.now())

    # Get Raw HTML
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    reg_url = "https://nvhealthresponse.nv.gov/"
    req = Request(url=reg_url, headers=headers) 
    html = urlopen(req).read() 
    soup = BeautifulSoup(html, "html.parser")
    g = open('{}/{}.html'.format(raw_name, now), 'w')
    g.write(str(soup))
    g.close()

    # Using Selenium
    # driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get("https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9")
    time.sleep(10)
    
    out = {}

    # Go to previous page
    driver.find_element_by_xpath('//*[@id="pbiAppPlaceHolder"]/ui-view/div/div[2]/logo-bar/div/div/div/logo-bar-navigation/span/a[1]/i').click()
    time.sleep(2)
    # # Click left
    # driver.find_element_by_xpath('//*[@id="pbiAppPlaceHolder"]/ui-view/div/div[2]/logo-bar/div/div/div/logo-bar-navigation/span/a[1]/i').click()
    # time.sleep(2)

    # General Info
    out = getinfo("", out, driver, raw_name, now)

    # Go to next page
    driver.find_element_by_xpath('//*[@id="pbiAppPlaceHolder"]/ui-view/div/div[2]/logo-bar/div/div/div/logo-bar-navigation/span/a[3]/i').click()
    time.sleep(2)

    # Get county data
    out_county = []
    county_names = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[8]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[1]/*')
    county_tests = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[8]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[3]/*')
    county_cases = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[8]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[6]/*')
    county_deaths = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[8]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[8]/*')
    county_tested = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[8]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[4]/*')
    if len(county_names) != len(county_tests) or len(county_names) != len(county_cases) or len(county_names) != len(county_deaths) or len(county_names) != len(county_tested):
        raise Exception("Irregular county table")

    for name, test, case, death, tested in zip(county_names, county_tests, county_cases, county_deaths, county_tested):
        county = {
            "County Name": name.text,
            "Total Tests": test.text,
            "Total People Tested": tested.text,
            "Total Cases": case.text,
            "Total Deaths": death.text,
            "Scrape Time": now
        }
        out_county.append(county)
    
    # Raw
    driver.save_screenshot(raw_name + "/county_" + now + ".png")

    # # PCR testing by location
    # chart_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[8]/transform/div/div[3]/div')
    # driver.execute_script("arguments[0].scrollIntoView();", chart_div)
    # actionChains = ActionChains(driver)
    # actionChains.context_click(chart_div).pause(3).send_keys(Keys.DOWN).send_keys(Keys.ENTER).perform()
    # time.sleep(3)
    # # Show table
    # # show_table = driver.find_element_by_xpath('/html/body/div[5]/drop-down-list/ng-transclude/ng-repeat/drop-down-list-item/ng-transclude/ng-switch/div')
    # # show_table.click()
    # # time.sleep(4)
    #  # Get table
    # headers_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[8]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[3]/div/*')
    # values_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[8]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div/*')


    # if len(headers_div) == 0 or  len(values_div) == 0:
    #     raise Exception("No values or headers scraped for NV Testing")

    # if len(headers_div) != len(values_div):
    #     raise Exception("Lab Testing data not right")

    # expected_labs = ["UMC", "NSPHL", "SNPHL", "LabCorp", "Quest", "Quest", "CPL", "RRMC", "Other"]

    # for header, value in zip(headers_div, values_div):
    #     header_val = header.find_element_by_class_name('pivotTableCellWrap ').text
    #     val_val = value.text
    #     # print(header_val, val_val)
    #     if header_val not in expected_labs:
    #         raise Exception("Unexpected lab")
    #     out["Total Tested: Lab_" + header_val] = val_val

    # # Go back
    # driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[8]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    # time.sleep(2)

    # Go to next page
    driver.find_element_by_xpath('//*[@id="pbiAppPlaceHolder"]/ui-view/div/div[2]/logo-bar/div/div/div/logo-bar-navigation/span/a[3]/i').click()
    time.sleep(2)

    # # Age, Gender, Race/Ethnicity - Total tested
    filter_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div')
    filter_div.click()
    time.sleep(2)
    select_button = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/visual-container-header-modern/div/div[1]/div/visual-header-item-container/div/button')
    select_button.click()
    time.sleep(2)

    # Select 
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div').click()
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[5]/div/span').click()
    time.sleep(2)

    # Go back
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)

    out = get_age_gender_race(driver, out, "TotalTested_")

    # Age, Gender, Race/Ethnicity - Deaths
    # Filter elements
    filter_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div')
    filter_div.click()
    time.sleep(2)
    select_button = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/visual-container-header-modern/div/div[1]/div/visual-header-item-container/div/button')
    select_button.click()
    time.sleep(2)

    # Select 
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div').click()
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[2]/div/span').click()
    time.sleep(2)

    # Go back
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)

    out = get_age_gender_race(driver, out, "Deaths_")

    # Age, Gender, Race/Ethnicity - Negative Tests 
    # Filter elements
    filter_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div')
    filter_div.click()
    time.sleep(2)
    select_button = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/visual-container-header-modern/div/div[1]/div/visual-header-item-container/div/button')
    select_button.click()
    time.sleep(2)

    # Select 
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div').click()
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[4]/div/span').click()
    time.sleep(2)

    # Go back
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)

    out = get_age_gender_race(driver, out, "TotalNegative_")

    # # Age, Gender, Race/Ethnicity - Confirmed Cases
    # Filter elements
    filter_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div')
    filter_div.click()
    time.sleep(2)
    select_button = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/visual-container-header-modern/div/div[1]/div/visual-header-item-container/div/button')
    select_button.click()
    time.sleep(2)

    # Select 
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div').click()
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[1]/div/span').click()
    time.sleep(2)

    # Go back
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    time.sleep(2)

    out = get_age_gender_race(driver, out, "ConfirmedCases_")

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

    # # Get age
    # age_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[1]')
    # actionChains = ActionChains(driver)
    # actionChains.context_click(age_div).perform()
    # time.sleep(2)
    # show_table = driver.find_element_by_xpath('/html/body/div[6]/drop-down-list/ng-transclude/ng-repeat/drop-down-list-item/ng-transclude/ng-switch/div')
    # show_table.click()
    # time.sleep(2)
    # # Get table
    # headers_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/*')
    # values_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/*')

    # if len(headers_div) != len(values_div):
    #     raise Exception("Age data not right")

    # expected_ages = ["<10", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"]

    # # Add to Out
    # for header, val in zip (headers_div, values_div):
    #     header_val = header.find_element_by_class_name('pivotTableCellWrap ')
    #     val_val = val.find_element_by_class_name('pivotTableCellWrap ')
    #     head = (header_val.text).strip()
    #     if head not in expected_ages:
    #         raise Exception("Unexpected age headers")
    #     if str(head) == "<10":
    #         head = "0-9"
    #     elif str(head) == "70+":
    #         head = "70_plus"
    #     elif str(head) == "Not Reported":
    #         head = "Unknown"
    #     head = str(head).replace("-","_")
    #     out["Tests_Age_" + head] = val_val.text


    # # Get Gender data 
    # driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    # time.sleep(2)
    # gender_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[9]/transform/div/div[3]/div/visual-modern/div/div/div[1]')
    # actionChains = ActionChains(driver)
    # actionChains.context_click(gender_div).perform()
    # time.sleep(2)
    # show_table = driver.find_element_by_xpath('/html/body/div[6]/drop-down-list/ng-transclude/ng-repeat/drop-down-list-item/ng-transclude/ng-switch/div')
    # show_table.click()
    # time.sleep(2)
    # # Get table
    # headers_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[9]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/*')
    # values_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[9]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/*')

    # if len(headers_div) != len(values_div):
    #     raise Exception("Gender data not right")

    # expected_genders = ["Male", "Female"]
    # # Add to Out
    # for header, val in zip (headers_div, values_div):
    #     header_val = header.find_element_by_class_name('pivotTableCellWrap ')
    #     val_val = val.find_element_by_class_name('pivotTableCellWrap ')
    #     head = (header_val.text).strip()
    #     if head not in expected_genders:
    #         raise Exception("Unexpected Gender")
    #     if head == "Not Reported":
    #         head = "GenderUnknown"
    #     out["Test" + head] = val_val.text
    
    # # Get Race data 
    # driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[9]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button').click()
    # time.sleep(2)
    # race_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/div/visual-modern/div/div/div[1]')
    # actionChains = ActionChains(driver)
    # actionChains.context_click(race_div).perform()
    # time.sleep(2)
    # show_table = driver.find_element_by_xpath('/html/body/div[6]/drop-down-list/ng-transclude/ng-repeat/drop-down-list-item/ng-transclude/ng-switch/div')
    # show_table.click()
    # time.sleep(2)
    # # Get table
    # headers_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/*')
    # values_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/div/detail-visual-modern/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/*')

    # if len(headers_div) != len(values_div):
    #     raise Exception("Race data not right")

    # expected_races = ["White", "Hispanic", "Black", "Asian", "AIAN"]
    # # Add to Out
    # for header, val in zip (headers_div, values_div):
    #     header_val = header.find_element_by_class_name('pivotTableCellWrap ')
    #     val_val = val.find_element_by_class_name('pivotTableCellWrap ')
    #     head = (header_val.text).strip()
    #     if head not in expected_races:
    #         raise Exception("Unexpected Race/Ethnicity")
    #     out["Test" + head] = val_val.text
    



    # # Main page elements
    # main = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/div')
    # dropdown = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div')

    # # UMC
    # current_lab = "Lab_UMC_"
    # xpath = '/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[2]/div/span'
    
    # # Collect info
    # out = collect(current_lab, main, dropdown, xpath, out, driver)

    # # NSPHL
    # current_lab = "Lab_NSPHL_"
    # xpath = '/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[3]/div/span'
    # # Collect info
    # out = collect(current_lab, main, dropdown, xpath, out, driver)

    # # SNPHL
    # current_lab = "Lab_SNPHL_"
    # xpath = '/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[4]/div/span'
    # # Collect info
    # out = collect(current_lab, main, dropdown, xpath, out, driver)

    # # LabCorp
    # current_lab = "Lab_LabCorp_"
    # xpath = '/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[5]/div/span'
    # # Collect info
    # out = collect(current_lab, main, dropdown, xpath, out, driver)

    # # Quest
    # current_lab = "Lab_Quest_"
    # xpath = '/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[6]/div/span'
    # # Collect info
    # out = collect(current_lab, main, dropdown, xpath, out, driver)

    # # CPL
    # current_lab = "Lab_CPL_"
    # xpath = '/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[7]/div/span'
    # # Collect info
    # out = collect(current_lab, main, dropdown, xpath, out, driver)

    # # RRMC
    # current_lab = "Lab_RRMC_"
    # xpath = '/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[8]/div/span'
    # # Collect info
    # out = collect(current_lab, main, dropdown, xpath, out, driver)

    # # Other
    # current_lab = "Lab_Other_"
    # xpath = '/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[9]/div/span'
    # # Collect info
    # out = collect(current_lab, main, dropdown, xpath, out, driver)

    # # Collect Age and Gender data
    # gotoOther(main, dropdown, driver)
    # # Select all
    # all_select = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div[1]/div/div/div[1]/div/span')
    # all_select.click()
    # # Go back
    # return_button = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[7]/transform/div/div[3]/visual-container-pop-out-bar/div/div[1]/button')
    # goback(return_button)
    # # Go to next page
    # driver.find_element_by_xpath('//*[@id="pbiAppPlaceHolder"]/ui-view/div/div[2]/logo-bar/div/div/div/logo-bar-navigation/span/a[3]/i').click()
    # time.sleep(2)

    # params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"s","Entity":"Sheet1"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Negative"}},"Function":0},"Name":"Sum(Sheet1.Negative)"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"RESULT"}}],"Values":[[{"Literal":{"Value":"'Total'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"s\",\"Entity\":\"Sheet1\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Negative\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.Negative)\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"RESULT\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Total'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Top\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"23b35406-eaa1-4c4c-9270-c9c5978432c6","Sources":[{"ReportId":"18636c78-00fa-41b0-8364-136fc9a8041e"}]}}],"cancelQueries":[],"modelId":272235}
    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "c425096e-ebb7-7750-d91d-a8b530e4c344", "RequestId": "307fe974-24bd-f876-325f-865f4cb64d4a", "X-PowerBI-ResourceKey": "206e8b9e-3ae5-40f9-afb5-6d05477897b6", "Origin": "https://app.powerbigov.us", "Referer": "https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9"}
    # negTests = requests.post("https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true", json=params, headers=headers).json()
    # with open("%s/negTests_%s.json" % (raw_name, now), "w") as fp:
    #     json.dump(negTests, fp)
    # out["PatientsNegative"] = int(negTests["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"])

    # params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"s","Entity":"Sheet1"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Male"}},"Function":0},"Name":"Sum(Sheet1.Male)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Female "}},"Function":0},"Name":"Sum(Sheet1.Female )"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Unknown"}},"Function":0},"Name":"Sum(Sheet1.Unknown)"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"RESULT"}}],"Values":[[{"Literal":{"Value":"'Total'"}}]]}}}],"OrderBy":[{"Direction":2,"Expression":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Male"}},"Function":0}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1,2]}]},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"s\",\"Entity\":\"Sheet1\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Male\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.Male)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Female \"}},\"Function\":0},\"Name\":\"Sum(Sheet1.Female )\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Unknown\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.Unknown)\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"RESULT\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Total'\"}}]]}}}],\"OrderBy\":[{\"Direction\":2,\"Expression\":{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Male\"}},\"Function\":0}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0,1,2]}]},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"23b35406-eaa1-4c4c-9270-c9c5978432c6","Sources":[{"ReportId":"18636c78-00fa-41b0-8364-136fc9a8041e"}]}}],"cancelQueries":[],"modelId":272235}
    # # Only RequestId changes
    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "c425096e-ebb7-7750-d91d-a8b530e4c344", "RequestId": "5c33263a-b0f1-9b6a-c167-cca127fca398", "X-PowerBI-ResourceKey": "206e8b9e-3ae5-40f9-afb5-6d05477897b6", "Origin": "https://app.powerbigov.us", "Referer": "https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9"}
    # gender = requests.post("https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true", json=params, headers=headers).json()
    # with open("%s/gender_%s.json" % (raw_name, now), "w") as fp:
    #     json.dump(gender, fp)
    # gtype = [x["Name"].replace(" ", "") for x in gender["results"][0]["result"]["data"]["descriptor"]["Select"]]
    # gvec = [int(x) for x in gender["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["C"]]
    # gmap = {'Sum(Sheet1.Male)': "TestMale", 'Sum(Sheet1.Female)': "TestFemale", 'Sum(Sheet1.Unknown)': "TestGenderUnknown"}
    # for tt, val in zip(gtype, gvec):
    #     out[gmap[tt]] = val
    # if " ".join(sorted(gtype)) != " ".join(sorted([x for x in gmap])):
    #     raise Exception("Unexpected gender in NV")

    # params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"s","Entity":"Sheet1"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"<10"}},"Function":0},"Name":"Sum(Sheet1.<10)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"70+"}},"Function":0},"Name":"Sum(Sheet1.70+)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Unknown Age"}},"Function":0},"Name":"Sum(Sheet1.Unknown Age)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"10-19"}},"Function":0},"Name":"Sum(Sheet1.10-19)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"20-29"}},"Function":0},"Name":"Sum(Sheet1.20-29)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"30-39"}},"Function":0},"Name":"Sum(Sheet1.30-39)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"40-49"}},"Function":0},"Name":"Sum(Sheet1.40-49)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"50-59"}},"Function":0},"Name":"Sum(Sheet1.50-59)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"60-69"}},"Function":0},"Name":"Sum(Sheet1.60-69)"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"RESULT"}}],"Values":[[{"Literal":{"Value":"'Total'"}}]]}}}],"OrderBy":[{"Direction":2,"Expression":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"<10"}},"Function":0}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1,2,3,4,5,6,7,8]}]},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"s\",\"Entity\":\"Sheet1\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"<10\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.<10)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"70+\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.70+)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Unknown Age\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.Unknown Age)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"10-19\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.10-19)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"20-29\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.20-29)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"30-39\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.30-39)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"40-49\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.40-49)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"50-59\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.50-59)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"60-69\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.60-69)\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"RESULT\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Total'\"}}]]}}}],\"OrderBy\":[{\"Direction\":2,\"Expression\":{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"<10\"}},\"Function\":0}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0,1,2,3,4,5,6,7,8]}]},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"23b35406-eaa1-4c4c-9270-c9c5978432c6","Sources":[{"ReportId":"18636c78-00fa-41b0-8364-136fc9a8041e"}]}}],"cancelQueries":[],"modelId":272235}
    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "c425096e-ebb7-7750-d91d-a8b530e4c344", "RequestId": "fba48d55-96af-b3c6-ad60-481cd90b0944", "X-PowerBI-ResourceKey": "206e8b9e-3ae5-40f9-afb5-6d05477897b6", "Origin": "https://app.powerbigov.us", "Referer": "https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9"}
    # ageTests = requests.post("https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true", json=params, headers=headers).json()
    # with open("%s/ageTests_%s.json" % (raw_name, now), "w") as fp:
    #     json.dump(ageTests, fp)
    # atype = [x["Name"].replace(" ", "") for x in ageTests["results"][0]["result"]["data"]["descriptor"]["Select"]]
    # avec = [int(x) for x in ageTests["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["C"]]
    # amap = {'Sum(Sheet1.<10)': "Tests_Age_0_9", 'Sum(Sheet1.70+)': "Tests_Age_70_plus", 'Sum(Sheet1.UnknownAge)': "Tests_Age_Unknown", 'Sum(Sheet1.10-19)': "Tests_Age_10_19", 'Sum(Sheet1.20-29)': "Tests_Age_20_29", 'Sum(Sheet1.30-39)': "Tests_Age_30_39", 'Sum(Sheet1.40-49)': "Tests_Age_40_49", 'Sum(Sheet1.50-59)': "Tests_Age_50_59", 'Sum(Sheet1.60-69)': "Tests_Age_60_69"}
    # for tt, val in zip(atype, avec):
    #     out[amap[tt]] = val
    # if " ".join(sorted(atype)) != " ".join(sorted([x for x in amap])):
    #     raise Exception("Unexpected age group in NV")

    # params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"s","Entity":"Sheet1"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Positive"}},"Function":0},"Name":"Sum(Sheet1.Positive)"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"RESULT"}}],"Values":[[{"Literal":{"Value":"'Total'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"s\",\"Entity\":\"Sheet1\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Positive\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.Positive)\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"RESULT\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Total'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Top\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"23b35406-eaa1-4c4c-9270-c9c5978432c6","Sources":[{"ReportId":"18636c78-00fa-41b0-8364-136fc9a8041e"}]}}],"cancelQueries":[],"modelId":272235}
    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "c425096e-ebb7-7750-d91d-a8b530e4c344", "RequestId": "2d7937fc-feeb-b093-d0c9-d3de128e1978", "X-PowerBI-ResourceKey": "206e8b9e-3ae5-40f9-afb5-6d05477897b6", "Origin": "https://app.powerbigov.us", "Referer": "https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9"}
    # posTests = requests.post("https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true", json=params, headers=headers).json()
    # with open("%s/posTests_%s.json" % (raw_name, now), "w") as fp:
    #     json.dump(posTests, fp)
    # out["PatientsPositive"] = int(posTests["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"])

    # params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"s","Entity":"Sheet1"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Actual Tests"}},"Function":0},"Name":"Sum(Sheet1.Actual Tests)"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"RESULT"}}],"Values":[[{"Literal":{"Value":"'Total'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"s\",\"Entity\":\"Sheet1\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Actual Tests\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.Actual Tests)\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"RESULT\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Total'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Top\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"23b35406-eaa1-4c4c-9270-c9c5978432c6","Sources":[{"ReportId":"18636c78-00fa-41b0-8364-136fc9a8041e"}]}}],"cancelQueries":[],"modelId":272235}
    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "c425096e-ebb7-7750-d91d-a8b530e4c344", "RequestId": "c5a0f822-3568-dd3f-859e-c5ad16aa1436", "X-PowerBI-ResourceKey": "206e8b9e-3ae5-40f9-afb5-6d05477897b6", "Origin": "https://app.powerbigov.us", "Referer": "https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9"}
    # totalTests = requests.post("https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true", json=params, headers=headers).json()
    # with open("%s/totalTests_%s.json" % (raw_name, now), "w") as fp:
    #     json.dump(totalTests, fp)
    # out["TestsPerformed"] = int(totalTests["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"])

    # params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"Deaths"},{"Name":"s","Entity":"Sheet1"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Count"}},"Function":0},"Name":"Sum(Deaths.Count)"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"RESULT"}}],"Values":[[{"Literal":{"Value":"'Total'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"d\",\"Entity\":\"Deaths\"},{\"Name\":\"s\",\"Entity\":\"Sheet1\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"Count\"}},\"Function\":0},\"Name\":\"Sum(Deaths.Count)\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"RESULT\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Total'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Top\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"23b35406-eaa1-4c4c-9270-c9c5978432c6","Sources":[{"ReportId":"18636c78-00fa-41b0-8364-136fc9a8041e"}]}}],"cancelQueries":[],"modelId":272235}
    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "c425096e-ebb7-7750-d91d-a8b530e4c344", "RequestId": "48987be4-e945-de63-3eff-69cc1ec1a4da", "X-PowerBI-ResourceKey": "206e8b9e-3ae5-40f9-afb5-6d05477897b6", "Origin": "https://app.powerbigov.us", "Referer": "https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9"}
    # deaths = requests.post("https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true", json=params, headers=headers).json()
    # with open("%s/deaths_%s.json" % (raw_name, now), "w") as fp:
    #     json.dump(deaths, fp)
    # out["Deaths"] = int(deaths["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"])

    # params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"s","Entity":"Sheet1"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"People Tested"}},"Function":0},"Name":"Sum(Sheet1.People Tested)"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"RESULT"}}],"Values":[[{"Literal":{"Value":"'Total'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"s\",\"Entity\":\"Sheet1\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"People Tested\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.People Tested)\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"RESULT\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Total'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Top\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"23b35406-eaa1-4c4c-9270-c9c5978432c6","Sources":[{"ReportId":"18636c78-00fa-41b0-8364-136fc9a8041e"}]}}],"cancelQueries":[],"modelId":272235}
    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "c425096e-ebb7-7750-d91d-a8b530e4c344", "RequestId": "b26f4a5e-05b2-79bf-96af-36b202b8e5f6", "X-PowerBI-ResourceKey": "206e8b9e-3ae5-40f9-afb5-6d05477897b6", "Origin": "https://app.powerbigov.us", "Referer": "https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9"}
    # peopleTested = requests.post("https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true", json=params, headers=headers).json()
    # with open("%s/peopleTested_%s.json" % (raw_name, now), "w") as fp:
    #     json.dump(peopleTested, fp)
    # out["PeopleTested"] = int(peopleTested["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"])

    # params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"s","Entity":"Sheet1"},{"Name":"k","Entity":"Key"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Positive"}},"Function":0},"Name":"CountNonNull(Sheet1.Positive)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Negative"}},"Function":0},"Name":"CountNonNull(Sheet1.Negative)"},{"Column":{"Expression":{"SourceRef":{"Source":"k"}},"Property":"Abbr"},"Name":"Key.Abbr"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"RESULT"}}],"Values":[[{"Literal":{"Value":"'Total'"}}]]}}}],"OrderBy":[{"Direction":1,"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"k"}},"Property":"Abbr"}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[2,0,1]}]},"DataReduction":{"DataVolume":4,"Primary":{"Window":{"Count":1000}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"s\",\"Entity\":\"Sheet1\"},{\"Name\":\"k\",\"Entity\":\"Key\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Positive\"}},\"Function\":0},\"Name\":\"CountNonNull(Sheet1.Positive)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Negative\"}},\"Function\":0},\"Name\":\"CountNonNull(Sheet1.Negative)\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"k\"}},\"Property\":\"Abbr\"},\"Name\":\"Key.Abbr\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"RESULT\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Total'\"}}]]}}}],\"OrderBy\":[{\"Direction\":1,\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"k\"}},\"Property\":\"Abbr\"}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[2,0,1]}]},\"DataReduction\":{\"DataVolume\":4,\"Primary\":{\"Window\":{\"Count\":1000}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"23b35406-eaa1-4c4c-9270-c9c5978432c6","Sources":[{"ReportId":"18636c78-00fa-41b0-8364-136fc9a8041e"}]}}],"cancelQueries":[],"modelId":272235}
    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "c425096e-ebb7-7750-d91d-a8b530e4c344", "RequestId": "152700f8-9421-077f-0985-618bcac9ace2", "X-PowerBI-ResourceKey": "206e8b9e-3ae5-40f9-afb5-6d05477897b6", "Origin": "https://app.powerbigov.us", "Referer": "https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9"}
    # resultsByLab = requests.post("https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true", json=params, headers=headers).json()
    # with open("%s/resultsByLab_%s.json" % (raw_name, now), "w") as fp:
    #     json.dump(resultsByLab, fp)
    # expected = " ".join(sorted(['NSPHL', 'SNPHL', 'LabCorp', 'Quest', 'CPL', 'Other', 'RRMC', 'UMC']))
    # rblDict = resultsByLab["results"][0]["result"]["data"]["dsr"]["DS"][0]["ValueDicts"]["D0"]
    # rblType = []
    # rblVal = []
    # for x in resultsByLab["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]:
    #     if len(x["C"]) == 2:
    #         rblType.append("Blank")
    #         rblVal.append((x["C"][0], x["C"][1]))
    #     elif len(x["C"]) == 3:
    #         rblType.append(rblDict[int(x["C"][0])])
    #         rblVal.append((x["C"][1], x["C"][2]))
    #     else:
    #         raise Exception("Unexpected structure in Nevada RBL")
    # if " ".join(sorted(rblType)) != expected:
    #     print("Observed types:", rblType)
    #     print("Expected types:", expected)
    #     print("JSON results:", resultsByLab["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"])
    #     print("JSON keys:", rblDict)
    #     raise Exception("Unexpected set of testing providers (results by lab) in Nevada")
    # for tt, val in zip(rblType, rblVal):
    #     out["Lab_%s_PatientPositive" % tt] = int(val[0])
    #     out["Lab_%s_PatientNegative" % tt] = int(val[1])

    # params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"s","Entity":"Sheet1"},{"Name":"k","Entity":"Key"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"Actual Tests"}},"Function":0},"Name":"Sum(Sheet1.Actual Tests)"},{"Column":{"Expression":{"SourceRef":{"Source":"k"}},"Property":"Abbr"},"Name":"Key.Abbr"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"RESULT"}}],"Values":[[{"Literal":{"Value":"'Total'"}}]]}}}],"OrderBy":[{"Direction":1,"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"k"}},"Property":"Abbr"}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[1,0]}]},"DataReduction":{"DataVolume":4,"Primary":{"Window":{"Count":1000}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"s\",\"Entity\":\"Sheet1\"},{\"Name\":\"k\",\"Entity\":\"Key\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"Actual Tests\"}},\"Function\":0},\"Name\":\"Sum(Sheet1.Actual Tests)\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"k\"}},\"Property\":\"Abbr\"},\"Name\":\"Key.Abbr\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"s\"}},\"Property\":\"RESULT\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Total'\"}}]]}}}],\"OrderBy\":[{\"Direction\":1,\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"k\"}},\"Property\":\"Abbr\"}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[1,0]}]},\"DataReduction\":{\"DataVolume\":4,\"Primary\":{\"Window\":{\"Count\":1000}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"23b35406-eaa1-4c4c-9270-c9c5978432c6","Sources":[{"ReportId":"18636c78-00fa-41b0-8364-136fc9a8041e"}]}}],"cancelQueries":[],"modelId":272235}
    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "c425096e-ebb7-7750-d91d-a8b530e4c344", "RequestId": "bc087558-82bb-124f-9c97-5e23f20183b9", "X-PowerBI-ResourceKey": "206e8b9e-3ae5-40f9-afb5-6d05477897b6", "Origin": "https://app.powerbigov.us", "Referer": "https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9"}
    # testsByLab = requests.post("https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true", json=params, headers=headers).json()
    # with open("%s/testsByLab_%s.json" % (raw_name, now), "w") as fp:
    #     json.dump(testsByLab, fp)
    # expected = " ".join(sorted(['NSPHL', 'SNPHL', 'LabCorp', 'Quest', 'CPL', 'Other', 'RRMC', 'UMC']))
    # tblDict = testsByLab["results"][0]["result"]["data"]["dsr"]["DS"][0]["ValueDicts"]["D0"]
    # tblType = []
    # tblVal = []
    # for x in testsByLab["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]:
    #     if len(x["C"]) == 1:
    #         continue
    #         # tblType.append("Blank")
    #         # tblVal.append(x["C"][0])
    #     elif len(x["C"]) == 2:
    #         tblType.append(tblDict[int(x["C"][0])])
    #         tblVal.append(x["C"][1])
    #     else:
    #         raise Exception("Unexpected total test format in Nevada")
    # if " ".join(sorted(tblType)) != expected:
    #     print("Observed types:", tblType)
    #     print("Expected types:", expected)
    #     print("JSON results:", testsByLab["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"])
    #     print("JSON keys:", tblDict)
    #     raise Exception("Unexpected set of testing providers (tests by lab) in Nevada")
    # for tt, val in zip(tblType, tblVal):
    #     out["Lab_%s_TotalTests" % tt] = int(val)
    # if not "Lab_Quest_TotalTests" in out:
    #     out["Lab_Quest_TotalTests"] = None

    

if __name__ == '__main__':
    run_NV({})
