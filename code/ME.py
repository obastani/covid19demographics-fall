from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys
from urllib.request import urlopen
import os
# from johnutil.imgutil import getGraph, getCanvas, getColors, getStackedGraph
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pytesseract
import base64
from io import BytesIO
from PIL import Image

def getCanvas(x, driver, flipBW = False):
    b64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", x)
    img = Image.open(BytesIO(base64.b64decode(b64)))
    if flipBW:
        pix = img.load()
        cols, rows = img.size  # indexing is backward...
        for r in range(rows):
            for c in range(cols):
                if pix[c,r][:3] == (255, 255, 255):
                    pix[c,r] = (0, 0, 0, 255)
                elif pix[c,r][:3] == (0, 0, 0):
                    pix[c,r] = (255, 255, 255, 255)
    return pytesseract.image_to_string(img)

def run_ME(args):
    # Parameters
    raw_name = '../ME/raw'
    data_name = '../ME/data/data.csv'
    now = str(datetime.now())

    # # Using Selenium
    # driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get("https://public.tableau.com/profile/maine.cdc.covid.19.response#!/vizhome/case-tables-and-summaries/cases-by-age")
    time.sleep(5)
    
    out = {}

    # Age
    driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="ng-app"]/body/div[1]/div[2]/section/div/div[2]/section[2]/figure/js-api-viz/div/iframe'))
    driver.save_screenshot(raw_name + "/" + now + "_cases-by-age.png")
    
    age_canvas = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId3"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver, False).replace(",", "")
    vals_canvas = getCanvas(driver.find_element_by_xpath('//*[@id="view768386095485213162_16337185235168260091"]/div[1]/div[2]/canvas[1]'), driver, False).replace(",", "")
    headers_canvas = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId3"]/div/div/div/div[1]/div[8]/div[1]/canvas'), driver, False).replace(",", "")

    headers = headers_canvas.replace(" ", "")
    if headers != "CasesShareofcases":
        raise Exception("Check age table headers")

    exp_ages = ['<20', '20s', '30s', '40s', '50s', '60s', '70s', '80+', '110s']
    age_cats = [x for x in age_canvas.split("\n") if x != ""]
    
    # Error Proofing
    if len(exp_ages) != len(age_cats):
        raise Exception("Unexpected number of age categories")

    unk_idx = -1

    if age_cats[len(age_cats) - 1] == "110s":
        unk_idx = len(age_cats) - 1
    else:
        raise Exception("Unexpected index for 110s age")

    for i in range(len(age_cats)):
        if exp_ages[i] != age_cats[i]:
            raise Exception("Unexpected value of age cats or unexpected order")

    vals = vals_canvas.split('\n')
    abs_val = []
    pct_val = []
    count = 0
    # Adjusted to put a dummy variable for last abs val because of single digit 
    for val in vals:
        # if count == unk_idx:
        #     plus_val = None
        #     try:
        #         plus_val = int(input('Abs Value for Cases for 110s? '))
        #     except:
        #         raise('Invalid input for 110s abs cases value')
        #     abs_val.append(plus_val)
        #     count += 1
        #     continue
        if val != '':
            if '%' in val:
                pct_val.append(val.strip('%'))
            else:
                abs_val.append(val)
        count += 1

    # Appending Cases for 110s
    if unk_idx == len(abs_val):
        plus_val = None
        try:
            plus_val = int(input('Abs Value for Cases 110s? '))
        except:
            raise('Invalid input for Abs Cases 110s')
        abs_val.append(plus_val)
    else:
        raise('Wrong position for 110s or did not read the right number of ages')
    
    # Error Proofing
    if len(abs_val) != len(pct_val):
        print(abs_val, pct_val)
        raise Exception("Unequal number of % and Abs values in Age table")
    if len(age_cats) != len(abs_val):
        raise Exception("Unequal number of age categories and values")

    # Mapping to help when consolidating
    mapping = {
        '<20': "Age [0-19]",
        '20s': "Age [20-29]",
        '30s': "Age [30-39]",
        '40s': "Age [40-49]",
        '50s': "Age [50-59]",
        '60s': "Age [60-69]",
        '70s': "Age [70-79]",
        '80+': "Age [80+]",
        '110s': "Age [110+]"
        # "unknown": "Unknown Age"
    }
    # Add to out
    for age, case, pct_case in zip(age_cats, abs_val, pct_val):
        # if mapping[age] == "Unknown Age":
        #     print("Please fill in the values manually:\n")
        #     out["# Cases " + mapping[age]] = float(input("Number of Unknown Age Cases? "))
        #     out["% Cases " + mapping[age]] = float(input("% of Unknown Cases? "))
        #     continue
        out["# Cases " + mapping[age]] = case
        out["% Cases " + mapping[age]] = pct_case
    
    # Gender
    driver.get("https://public.tableau.com/profile/maine.cdc.covid.19.response#!/vizhome/case-tables-and-summaries/cases-by-sex")
    time.sleep(5)
    driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="ng-app"]/body/div[1]/div[2]/section/div/div[2]/section[2]/figure/js-api-viz/div/iframe'))
    driver.save_screenshot(raw_name + "/" + now + "_cases-by-sex.png")

    sex_canvas = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId3"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver, False).replace(",", "")
    vals_canvas = getCanvas(driver.find_element_by_xpath('//*[@id="view11893188989390187402_11591262500339776443"]/div[1]/div[2]/canvas[1]'), driver, False).replace(",", "")
    headers_canvas = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId3"]/div/div/div/div[1]/div[8]/div[1]/canvas'), driver, False).replace(",", "")
    
    headers = headers_canvas.replace(" ", "")
    if headers != "CasesConfirmedcasesProbablecasesDeathsHospitalizationsRecoveries":
        raise Exception("Check sex table headers")
    
    exp_sex = ['Female', 'Male']
    sex_cats = sex_canvas.split('\n')

    # Removing blanks from list
    while("" in sex_cats) : 
        sex_cats.remove("")
    
    if len(exp_sex) != len(sex_cats):
        raise Exception("Unequal number of sex categories")
    for i in range(len(exp_sex)):
        if exp_sex[i] != sex_cats[i]:
            raise Exception("Different order of sex categories in sex table")

    vals = vals_canvas.split('\n')
    female_vals = vals[0].split(" ")
    male_vals = vals[1].split(" ")
    sex_vals = {
        "Female": female_vals,
        "Male": male_vals
    }

    if len(female_vals) != len(male_vals):
        raise Exception("Unequal number of values for each sex")

    for sex in sex_cats:
        out["Total Cases: " + sex] = sex_vals[sex][0]
        out["Total Confirmed Cases: " + sex] = sex_vals[sex][1]
        out["Total Probable Cases: " + sex] = sex_vals[sex][2]
        out["Total Deaths: " + sex] = sex_vals[sex][3]
        out["Total Hospitalized: " + sex] = sex_vals[sex][4]
        out["Total Recovered: " + sex] = sex_vals[sex][5]

    # Race/Ethnicity
    driver.get('https://public.tableau.com/profile/maine.cdc.covid.19.response#!/vizhome/case-tables-and-summaries/cases-by-race-and-ethnicity')
    time.sleep(5)
    driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="ng-app"]/body/div[1]/div[2]/section/div/div[2]/section[2]/figure/js-api-viz/div/iframe'))
    exp_races = ['American Indian or Alaska Native', 'Asian', 'Black or African American', 'White', 'Two or more', 'Other Race', 'Native Hawaiian or Other Pacific Islander', 'Not disclosed']
    driver.save_screenshot(raw_name + "/" + now + "_cases-by-race-and-ethnicity.png")
    driver.close()
    print("Please open: https://public.tableau.com/profile/maine.cdc.covid.19.response#!/vizhome/case-tables-and-summaries/cases-by-race-and-ethnicity")
    ans = input("Look at the race-ethnicity table. Are there 8 races? y or n ")
    if ans.strip() == 'y':
        print("Please fill in the values manually:")
        for race in exp_races:
            if race == "Not disclosed":
                out["# Cases Race/Ethnicity: Unknown Race"] = input(race + "? ")
            else:
                out["# Cases Race/Ethnicity: " + race ] = input(race + "? ")
    else:
        raise Exception("Unexpected Race")

    exp_ethns = ['Hispanic or Latino', "Not Hispanic or Latino", "Unknown"]
    ans = input("Now look at the ethnicity table. Are there 3 Ethnicities? y or n ")
    if ans.strip() == 'y':
        print("Please fill in the values manually: ")
        for ethn in exp_ethns:
            if ethn == "Unknown":
                out["# Cases Race/Ethnicity: Unknown Ethnicity"] = input(ethn + "? ")
            else:
                out["# Cases Race/Ethnicity: " + ethn] = input(ethn + "? ")
    else:
        raise Exception("Unexpected Ethnicity")

    # Output
    out["Scrape_Time"] = now
    fields = sorted([x for x in out])
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])

    # # Open file
    # exists = os.path.exists(data_name)
    # f = open(data_name, 'a')
    # writer = csv.writer(f)
    # if not exists:
    #     writer.writerow(["Age [0-19]", "Age [20-29]", "Age [30-39]",
    #                      "Age [40-49]", "Age [50-59]", "Age [60-69]",
    #                      "Age [70-79]", "Age [80+]", "Female", "Male",
    #                      "# Cases Race/Ethnicity: American Indian or Alaskan Native",
    #                      "# Cases Race/Ethnicity: Asian or Pacific Islander",
    #                      "# Cases Race/Ethnicity: Black or African American",
    #                      "# Cases Race/Ethnicity: White",
    #                      "# Cases Race/Ethnicity: Multiple Races",
    #                      "# Cases Race/Ethnicity: Other Race",
    #                      "# Cases Race/Ethnicity: Unknown Race",
    #                      "# Cases Race/Ethnicity: Hispanic",
    #                      "# Cases Race/Ethnicity: Not Hispanic",
    #                      "# Cases Race/Ethnicity: Unknown Ethnicity",
    #                      "pullTime"])

    # # Scrape data
    # now = datetime.now()
    # html = urlopen("https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus/data.shtml").read()
    # soup = BeautifulSoup(html, "html.parser")
    # g = open('{}/{}.html'.format(raw_name, now), 'w')
    # g.write(str(soup))
    # g.close()

    # # Get age distribution
    # age1 = float(list(list(list(soup(text='<20')[0].parent.parent.children)[5].children)[0].children)[0][:-1])/100
    # age2 = float(list(list(list(soup(text='20s')[0].parent.parent.children)[5].children)[0].children)[0][:-1])/100
    # age3 = float(list(list(list(soup(text='30s')[0].parent.parent.children)[5].children)[0].children)[0][:-1])/100
    # age4 = float(list(list(list(soup(text='40s')[0].parent.parent.children)[5].children)[0].children)[0][:-1])/100
    # age5 = float(list(list(list(soup(text='50s')[0].parent.parent.children)[5].children)[0].children)[0][:-1])/100
    # age6 = float(list(list(list(soup(text='60s')[0].parent.parent.children)[5].children)[0].children)[0][:-1])/100
    # age7 = float(list(list(list(soup(text='70s')[0].parent.parent.children)[5].children)[0].children)[0][:-1])/100
    # age8 = float(list(list(list(soup(text='80+')[0].parent.parent.children)[5].children)[0].children)[0][:-1])/100

    # # Get gender distribution
    # female = float(list(list(list(soup(text='Female')[0].parent.parent.children)[5].children)[0].children)[0][:-1])/100
    # male = float(list(list(list(soup(text='Male')[0].parent.parent.children)[5].children)[0].children)[0][:-1])/100
    
    # # Get race distribution
    # aian_cases = float((list(list(soup(text="American Indian or Alaskan Native")[0].parent.parent.children)[3].children)[0]).replace(',',""))
    # aipi_cases = float((list(list(soup(text="Asian or Pacific Islander")[0].parent.parent.children)[3].children)[0]).replace(',',""))
    # black_cases = float((list(list(soup(text="Black or African American")[0].parent.parent.children)[3].children)[0]).replace(',',""))
    # white_cases = float((list(list(soup(text="White")[0].parent.parent.children)[3].children)[0]).replace(',',""))
    # multiple_cases = float((list(list(soup(text="Two or More")[0].parent.parent.children)[3].children)[0]).replace(',',""))
    # other_cases = float((list(list(soup(text="Other")[0].parent.parent.children)[3].children)[0]).replace(',',""))
    # unknown_cases = float((list(list(soup(text="Not Disclosed")[0].parent.parent.children)[3].children)[0]).replace(',',""))

    # # Get ethnicity distribution
    # hisp_cases = float((list(list(soup(text="Hispanic")[0].parent.parent.children)[3].children)[0]).replace(',',""))
    # non_hisp_cases = float((list(list(soup(text="Not Hispanic")[0].parent.parent.children)[3].children)[0]).replace(',',""))
    # unknown_eth_cases = float((list(list(soup(text="Not Disclosed")[1].parent.parent.children)[3].children)[0]).replace(',',""))


    # # Write row
    # writer.writerow([age1, age2, age3, age4, age5, age6, age7, age8, female,
    #                  male, aian_cases, aipi_cases, black_cases, white_cases,
    #                  multiple_cases, other_cases, unknown_cases, hisp_cases,
    #                  non_hisp_cases, unknown_eth_cases, now])

    # # Close file
    # f.close()

if __name__ == '__main__':
    run_ME({})
