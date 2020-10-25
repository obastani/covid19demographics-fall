from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys
from urllib.request import urlopen, Request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import time

def export_county(out_county, data_name):
    for county in out_county:
        fields = sorted([x for x in county])
        exists = os.path.exists(data_name)
        with open(data_name, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([county[x] for x in fields])

def export(out, data_name):
    fields = [x for x in out]
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])

def run_new_scrape():
    # Parameters
    now = str(datetime.now())
    raw_name = '../SD/raw'
    data_name = '../SD/data/data.csv'

    # Get Raw File
    reg_url = 'https://doh.sd.gov/news/Coronavirus.aspx'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url=reg_url, headers=headers) 
    html = urlopen(req).read() 
    soup = BeautifulSoup(html, "html.parser")
    g = open('{}/{}.html'.format(raw_name, now), 'w')
    g.write(str(soup))
    g.close()

    # Using Selenium
    # driver = webdriver.Safari()
    url = soup.findAll('iframe')[1]['src']
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get(url)
    time.sleep(10)
    # Change focus
    # frame = driver.find_element_by_xpath('//*[@id="content_block"]/iframe')
    # driver.switch_to.frame(frame)
    # wait = WebDriverWait(driver, 10)
    # element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[11]/transform/div/div[3]/div/visual-modern/div/button')))
    # element.click()
    # time.sleep(10)  # More robust to wait for elements to appear...

    # Click - Tables tab
    # driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[2]/transform/div/div[3]/div/visual-modern/div/button').click()
    driver.find_element_by_xpath('//*[@id="pbiAppPlaceHolder"]/ui-view/div/div[2]/logo-bar/div/div/div/logo-bar-navigation/span/a[3]/i').click()
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="pbiAppPlaceHolder"]/ui-view/div/div[2]/logo-bar/div/div/div/logo-bar-navigation/span/a[3]/i').click()
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="pbiAppPlaceHolder"]/ui-view/div/div[2]/logo-bar/div/div/div/logo-bar-navigation/span/a[3]/i').click()
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="pbiAppPlaceHolder"]/ui-view/div/div[2]/logo-bar/div/div/div/logo-bar-navigation/span/a[3]/i').click()
    time.sleep(20)

    expected_cats = ["# of Cases", "# of Deaths", "% of Cases"]
    expected_cats_county = ["Positive Cases", "Recovered Cases", "Negative Persons", "Deceased"]
    expected_table1_fields = ["Active Cases", "Currently Hospitalized", "Recovered Cases", "Total Cases", "Total Persons Negative", "Ever Hospitalized", "Deaths"]
    expected_ages = ["0-9 years", "10-19 years", "20-29 years", "30-39 years", "40-49 years", "50-59 years", "60-69 years", "70-79 years", "80+ years"]
    expected_sexes = ["Female", "Male"]
    expected_races = ["Unknown, Non-Hispanic", "Black, Non-Hispanic", "Hispanic", "Native American, Non-Hispanic", "Other, Non-Hispanic", "White, Non-Hispanic", "Asian, Non-Hispanic"]

    # Table 1 - COVID-19 in South Dakota
    out = {}

    table1_field_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[4]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[1]/*')
    table1_val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[4]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[2]/*')
    
    # Check both divs are the same size
    if len(table1_field_div) != len(table1_val_div):
        raise Exception("Size of table1 fields != table1 values")
    
    for el_field, el_val in zip(table1_field_div, table1_val_div):
        if el_field.text not in expected_table1_fields:
            raise Exception("Unexpected field in Table 1 " + el_field.text)
        out[el_field.text] = el_val.text
    
    # Table 2 - Age
    ages_val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[1]/*')
    cases_val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[2]/*')
    deaths_val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[3]/*')
    cases_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[2]/div[@title]').text).strip()
    deaths_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[5]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[3]/div[@title]').text).strip()

    if cases_header not in expected_cats:
        raise Exception("Unexpected # of Cases Header")
    if deaths_header not in expected_cats:
         raise Exception("Unexpected # of Deaths Header")
    if len(ages_val_div) != len(cases_val_div) or len(deaths_val_div) != len(cases_val_div) or len(ages_val_div) != len(deaths_val_div):
        raise Exception("Size of table fields and values are not the same in table 2")

    for ages_el, cases_el, deaths_el in zip(ages_val_div, cases_val_div, deaths_val_div):
        if ages_el.text not in expected_ages:
            raise Exception("Unexpected age category in table 2")
        out[cases_header + ": " + ages_el.text] = cases_el.text
        out[deaths_header + ": " + ages_el.text] = deaths_el.text
        
   # Table 3 - Sex
    sex_val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[1]/*')
    cases_val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[2]/*')
    deaths_val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[3]/*')
    cases_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[2]/div[@title]').text).strip()
    deaths_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[3]/div[@title]').text).strip()

    if cases_header not in expected_cats:
        raise Exception("Unexpected # of Cases Header")
    if deaths_header not in expected_cats:
         raise Exception("Unexpected # of Deaths Header")
    if len(sex_val_div) != len(cases_val_div) or len(deaths_val_div) != len(cases_val_div) or len(sex_val_div) != len(deaths_val_div):
        raise Exception("Size of table fields and values are not the same in table 3")

    for sex_el, cases_el, deaths_el in zip(sex_val_div, cases_val_div, deaths_val_div):
        if sex_el.text not in expected_sexes:
            raise Exception("Unexpected sex category in table 3")
        out[cases_header + ": " + sex_el.text] = cases_el.text
        out[deaths_header + ": " + sex_el.text] = deaths_el.text
    
    # Table 4 - Race/Ethnicity
    race_val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[2]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[1]/*')
    cases_val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[2]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[2]/*')
    percent_val_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[2]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[3]/*')
    cases_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[2]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[2]/div[@title]').text).strip()
    percent_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[2]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[3]/div[@title]').text).strip()

    if cases_header not in expected_cats:
        raise Exception("Unexpected # of Cases Header")
    if percent_header not in expected_cats:
         raise Exception("Unexpected % of Cases Header")
    if len(race_val_div) != len(cases_val_div) or len(percent_val_div) != len(cases_val_div) or len(race_val_div) != len(percent_val_div):
        raise Exception("Size of table fields and values are not the same in table 4")

    count = 0
    for race_el, cases_el, percent_el in zip(race_val_div, cases_val_div, percent_val_div):
        count += 1
        race = race_el.get_attribute("title")
        if race not in expected_races:
            raise Exception("Unexpected race/ethnicity category in table 4: " + race)
        out[cases_header + ": " + race] = cases_el.text
        out[percent_header + ": " + race] = percent_el.text

    if count != len(expected_races):
        raise Exception("Unequal number of races")
    # Get county data
    out_county = []

    # County
    county_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[1]/div[@title]').text).strip()
    positive_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[2]/div[@title]').text).strip()
    recovered_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[3]/div[@title]').text).strip()
    negative_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[4]/div[@title]').text).strip()
    deaths_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[5]/div[@title]').text).strip()
    county_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div[3]/div[1]/*')
    positive_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div[3]/div[2]/*')
    recovered_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div[3]/div[3]/*')
    negative_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div[3]/div[4]/*')
    deaths_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[3]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div[3]/div[5]/*')
    
    if county_header != "County":
        raise Exception("Unexpected County Name header in County Deaths: " + county_header)
    if positive_header not in expected_cats_county:
        raise Exception("Unexpected Category in County Deaths: " + positive_header)
    if recovered_header not in expected_cats_county:
        raise Exception("Unexpected Category in County Deaths: " + recovered_header)
    if negative_header not in expected_cats_county:
        raise Exception("Unexpected Category in County Deaths: " + negative_header)
    if deaths_header not in expected_cats_county:
        raise Exception("Unexpected Category in County Deaths: " + deaths_header)
    if len(county_div) != len(deaths_div) or len(county_div) != len(positive_div) or len(county_div) != len(recovered_div) or len(county_div) != len(negative_div):
        raise Exception("Unequal number of values county")
    
    for county, positive, recovered, negative, death in zip(county_div, positive_div, recovered_div, negative_div, deaths_div):
        county_name = county.get_attribute("title")
        county_dict = {
            "County Name": str(county_name),
            "Total Positive Cases": str(positive.text),
            "Total Recovered Cases": str(recovered.text),
            "Total Negative Cases": str(negative.text),
            "Total Deaths": str(death.text),
            "Scrape Time": now
        }
        out_county.append(county_dict)
    
    # Export
    # data_county_death_name = "../SD/data/data_county_death.csv"
    # export_county(out_county_deaths, data_county_death_name)
    
    # # County Cases
    # county_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[1]/div[@title]').text).strip()
    # pos_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[2]/div[@title]').text).strip()
    # rev_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[3]/div[@title]').text).strip()
    # neg_header = (driver.find_element_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[2]/div/div[4]/div[@title]').text).strip()
    # exp_header = ['County', 'Positive Cases', 'Recovered Cases', 'Negative Cases']
    
    # if county_header not in exp_header or pos_header not in exp_header or\
    #      rev_header not in exp_header or neg_header not in exp_header:
    #         raise Exception("Unexpected header in County Cases")
    
    # county_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[1]/*')
    # pos_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[2]/*')
    # rec_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[3]/*')
    # neg_div = driver.find_elements_by_xpath('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas-modern/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-modern[6]/transform/div/div[3]/div/visual-modern/div/div/div[2]/div[1]/div[4]/div/div/div[4]/*')
    
    # if len(county_div) != len(pos_div) or len(county_div) != len(rec_div) or\
    #     len(county_div) != len(neg_div):
    #         raise Exception("Unequal number of row values in county cases tbl")
    
    # for county, pos, rec, neg in zip(county_div, pos_div, rec_div, neg_div):
    #     county_name = county.get_attribute("title")
    #     county_dict = {
    #         "County Name": county_name,
    #         "Total Positive Cases": pos.text,
    #         "Total Recovered Cases": rec.text,
    #         "Total Negative Cases": neg.text,
    #         "Scrape Time": now
    #     }
    #     out_county.append(county_dict)

    # Output County
    data_county_name = "../SD/data/data_county.csv"
    export_county(out_county, data_county_name)

    # Output
    out["Scrape Time"] = now
    export(out, data_name)

def run_SD(args):
    # broken = True
    # if broken:
    run_new_scrape()
    # exit()
    # # Parameters
    # raw_name = '../SD/raw'
    # data_name = '../SD/data/data.csv'

    # # Open file
    # exists = os.path.exists(data_name)
    # f = open(data_name, 'a')
    # writer = csv.writer(f)
    # if not exists:
    #     writer.writerow(["Age [0-19]: Cases", "Age [20-29]: Cases", "Age [30-39]: Cases", "Age [40-49]: Cases", "Age [50-59]: Cases", "Age [60-69]: Cases",
    #                      "Age [70-79]: Cases", "Age [80+]: Cases", "Age [0-19]: Deaths", "Age [20-29]: Deaths", "Age [30-39]: Deaths", "Age [40-49]: Deaths",
    #                      "Age [50-59]: Deaths", "Age [60-69]: Deaths", "Age [70-79]: Deaths", "Age [80+]: Deaths", "Male: Cases", "Female: Cases"
    #                      "Male: Deaths", "Female: Deaths", "pullTime"])

    # # Scrape data
    # now = datetime.now()
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    # reg_url = 'https://doh.sd.gov/news/Coronavirus.aspx'
    # req = Request(url=reg_url, headers=headers) 
    # html = urlopen(req).read() 
    # soup = BeautifulSoup(html, "html.parser")
    # g = open('{}/{}.html'.format(raw_name, now), 'w')
    # g.write(str(soup))
    # g.close()

    # # Get age distribution
    # age1c = int(list(list(list(soup(text='0 to 19 years')[0].parent.parent.parent.parent.children)[3].children)[0].children)[0])
    # age2c = int(list(list(list(soup(text='20 to 29 years')[0].parent.parent.parent.parent.children)[3].children)[0].children)[0])
    # age3c = int(list(list(list(soup(text='30 to 39 years')[0].parent.parent.parent.parent.children)[3].children)[0].children)[0])
    # age4c = int(list(list(list(soup(text='40 to 49 years')[0].parent.parent.parent.parent.children)[3].children)[0].children)[0])
    # age5c = int(list(list(list(soup(text='50 to 59 years')[0].parent.parent.parent.parent.children)[3].children)[0].children)[0])
    # age6c = int(list(list(list(soup(text='60 to 69 years')[0].parent.parent.parent.parent.children)[3].children)[0].children)[0])
    # age7c = int(list(list(list(soup(text='70 to 79 years')[0].parent.parent.parent.parent.children)[3].children)[0].children)[0])
    # age8c = int(list(list(list(soup(text='80+ years')[0].parent.parent.parent.parent.children)[3].children)[0].children)[0])

    # age1d = int(list(list(list(soup(text='0 to 19 years')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    # age2d = int(list(list(list(soup(text='20 to 29 years')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    # age3d = int(list(list(list(soup(text='30 to 39 years')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    # age4d = int(list(list(list(soup(text='40 to 49 years')[0].parent.parent.parent.parent.children)[5].children)[0].children)[0])
    # age5d = int(list(list(list(soup(text='50 to 59 years')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    # age6d = int(list(list(list(soup(text='60 to 69 years')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    # age7d = int(list(list(list(soup(text='70 to 79 years')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    # age8d = int(list(list(list(soup(text='80+ years')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])

    # # Get gender distribution
    # malec = int(list(list(list(soup(text='Male')[0].parent.parent.parent.parent.children)[3].children)[0].children)[0])
    # femalec = int(list(list(list(soup(text='Female')[0].parent.parent.parent.parent.children)[3].children)[0].children)[0])

    # maled = int(list(list(list(soup(text='Male')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    # femaled = int(list(list(list(soup(text='Female')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    
    # # Write row
    # writer.writerow([age1c, age2c, age3c, age4c, age5c, age6c, age7c, age8c, age1d, age2d, age3d, age4d, age5d, age6d, age7d, age8d,
    #                  malec, femalec, maled, femaled, now])

    # # Close file
    # f.close()

if __name__ == '__main__':
    run_SD({})
