# https://dhhr.wv.gov/COVID-19/Pages/default.aspx
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

def run_hist():
    # Using Selenium
    # driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get("https://dhhr.wv.gov/COVID-19/Pages/default.aspx")
    time.sleep(7)
    frame = driver.find_element_by_xpath('//*[@id="responsive"]/iframe')
    driver.execute_script("return arguments[0].scrollIntoView(true);", frame)
    driver.switch_to.frame(frame)
    time.sleep(2)

    out = {}
    
    # Click Positive Case Trends
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[17]/transform/div/div[3]/div/visual-modern/div/button').click()
    time.sleep(2)
    cum_cases_div = driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[4]/transform/div/div[3]/div/visual-modern/div')
    actionChains = ActionChains(driver)
    actionChains.context_click(cum_cases_div).pause(3).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    # Click Lab Test Trends
    
    # Click Hospital
    
def get_data(out_county, tables, county_list):
    now = str(datetime.now())
    for table in tables:
        sum_county = 0
        for segment in table[0]:
            vals = [x.text for x in segment.find_elements_by_xpath('.//*') if '\n' not in x.text]
            if table[1] == "Table 1":
                if len(vals) % 7 != 0:
                    raise Exception("Unequal number of columns")
                num_counties = len(vals)/7
                sum_county += num_counties
                cols = []
                col = []
                count = 0
                for val in vals:
                    count += 1
                    col.append(val)
                    if count == num_counties:
                        count = 0
                        cols.append(col)
                        col = []
                for col in cols:
                    if len(col) != num_counties:
                        raise Exception("Uneven number of values")
                for county, active, rec, conf, prob, test, death in zip(cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]):
                    if county in county_list:
                        continue
                    ct = {
                        "County Name": county,
                        "# Confirmatory Lab Tests": (test).replace(",",""),
                        "Total Probable Cases": (prob).replace(",",""),
                        "Total Confirmed Cases": (conf).replace(",",""),
                        "Total Active Cases": (active).replace(",",""),
                        "Total Recovered": (rec).replace(",",""),
                        "Total Deaths: ": (death).replace(",",""),
                        "Scrape Time": now
                    }
                    out_county.append(ct)
                    county_list.append(county)
            # elif table[1] == "Table 2":
            #     if len(vals) % 4 != 0:
            #          raise Exception("Unequal number of columns")
            #     num_counties = len(vals)/4
            #     sum_county += num_counties
            #     cols = []
            #     col = []
            #     count = 0
            #     for val in vals:
            #         count += 1
            #         col.append(val)
            #         if count == num_counties:
            #             count = 0
            #             cols.append(col)
            #             col = []
            #     for col in cols:
            #         if len(col) != num_counties:
            #             raise Exception("Uneven number of values")
            #     for f_cases, f_tests, m_cases, m_tests in zip(cols[0], cols[1], cols[2], cols[3]):
            #         out_county[idx]["Total Cases: Female"] = f_cases.replace(",","")
            #         out_county[idx]["Total Confirmatory Tests: Female"] = f_tests.replace(",","")
            #         out_county[idx]["Total Cases: Male"] = m_cases.replace(",","")
            #         out_county[idx]["Total Confirmatory Tests: Male"] = m_tests.replace(",","")
            #         idx += 1
            # elif table[1] == "Table 3":
            #     if len(vals) % 3 != 0:
            #          raise Exception("Unequal number of columns")
            #     num_counties = len(vals)/3
            #     sum_county += num_counties
            #     cols = []
            #     col = []
            #     count = 0
            #     for val in vals:
            #         count += 1
            #         col.append(val)
            #         if count == num_counties:
            #             count = 0
            #             cols.append(col)
            #             col = []
            #     for col in cols:
            #         if len(col) != num_counties:
            #             raise Exception("Uneven number of values")
            #     for black, other, white in zip(cols[0], cols[1], cols[2]):
            #         # out_county[idx]["% Cases Race/Ethnicity: Unknown"] = unk.replace("%","")
            #         out_county[idx]["% Cases Race/Ethnicity: Black"] = black.replace("%","")
            #         out_county[idx]["% Cases Race/Ethnicity: Other"] = other.replace("%","")
            #         out_county[idx]["% Cases Race/Ethnicity: White"] = white.replace("%","")
            #         out_county[idx]["Scrape Time"] = now
            #         idx += 1
        # if sum_county != 55:
        #     raise Exception("Unexpected number of counties: " + str(sum_county))
    return out_county, county_list
            


def run_WV(args):
    # run_hist()
    # exit()
    # Parameters
    raw_name = '../WV/raw'
    data_county = '../WV/data/data_county.csv'
    now = str(datetime.now())

    # Using Selenium
    # driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get("https://dhhr.wv.gov/COVID-19/Pages/default.aspx")
    time.sleep(7)
    frame = driver.find_element_by_xpath('//*[@id="responsive"]/iframe')
    driver.execute_script("return arguments[0].scrollIntoView(true);", frame)
    driver.switch_to.frame(frame)
    time.sleep(2)

    out_county = []

    # Get county data
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[9]/transform/div/div[2]/visual-container-modern[2]/transform/div/div[3]/div/visual-modern/div/button').click()
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[11]/transform/div/div[3]/div/visual-modern/div/button').click()
    time.sleep(3)
   
    table1_div = (driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[1]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/*'), 'Table 1')
    # table2_div = (driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[2]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/*'), 'Table 2')
    # table3_div = (driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/*'), 'Table 3')
    # Raw
    driver.save_screenshot(raw_name + "/county1_" + now + ".png")
    tables = [table1_div]
    county_list = []
    out_county, county_list = get_data(out_county, tables, county_list)
    driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[1]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[1]/div').click()
    time.sleep(3)
    # Raw
    driver.save_screenshot(raw_name + "/county2_" + now + ".png")
    table1_div = (driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[1]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/*'), 'Table 1')
    # table2_div = (driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[2]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/*'), 'Table 2')
    # table3_div = (driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/*'), 'Table 3')
    tables = [table1_div]
    out_county, county_list = get_data(out_county, tables, county_list)

    if len(county_list) != 55:
        raise Exception("Did not collect all counties")
    
    
    for county in out_county:
        fields = sorted([x for x in county])
        exists = os.path.exists(data_county)
        with open(data_county, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([county[x] for x in fields])

    # # Get Statewide
    # out = {}
    # driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[4]/transform/div/div[3]/div/visual-modern/div/button').click()
    # time.sleep(5)
    # out["Total Confirmed Cases"] = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[14]/transform/div/div[3]/div/visual-modern/div/svg/g[1]/text/tspan').text).replace(",","")
    # out["Total Probable Cases"] = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[16]/transform/div/div[3]/div/visual-modern/div/svg/g[1]/text/tspan').text).replace(",","")
    # out["Total Deaths"] = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[35]/transform/div/div[3]/div/visual-modern/div/svg/g[1]/text/tspan').text).replace(",","")
    # out["Total Recovered Cases"] = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[18]/transform/div/div[3]/div/visual-modern/div/svg/g[1]/text/tspan').text).replace(",","")
    # out["Total Active Cases"] = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[19]/transform/div/div[3]/div/visual-modern/div/svg/g[1]/text/tspan').text).replace(",","")

    # print(out)

    # Get Hospital (Daily confirmed hosp, confirmed icu, confirmed vent)

if __name__ == '__main__':
    run_WV({})
