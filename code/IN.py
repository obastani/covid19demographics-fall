import csv
from datetime import datetime
from io import BytesIO
from io import StringIO
import os
from PIL import Image
import pytesseract
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from urllib.request import urlopen, Request
import requests

def grabImg(url, fname):
    # Grab png
    r = requests.get(url)
    if not r.ok:
        raise Exception("Error accessing " + url)
    with open(fname, 'wb') as f:
        f.write(r.content)
    return Image.open(BytesIO(r.content))

def grabData(img, prefix, out):
    # Grab rectangles of correct colors
    cols, rows = img.size
    pix = img.load()
    batches = []
    currbatch = []
    for r in range(rows):
        rowmatch = False
        for c in range(cols):
            if (pix[c,r][0] >= 200 and pix[c,r][1] >= 100 and pix[c,r][2] <= 20) or (pix[c,r][0] >= 50 and pix[c,r][1] <= 10 and pix[c,r][2] <= 10):
                rowmatch = True
                currbatch.append((r, c))
        if not rowmatch and len(currbatch) > 0:
            batches.append((min([x[0] for x in currbatch]), max([x[0] for x in currbatch]), min([x[1] for x in currbatch]), max([x[1] for x in currbatch])))
            currbatch = []
    if len(currbatch) > 0:
        batches.append((min([x[0] for x in currbatch]), max([x[0] for x in currbatch]), min([x[1] for x in currbatch]), max([x[1] for x in currbatch])))

    # An age range may be missing a bar; let's fill it in
    if len(batches) < 10:
        currage = batches[:-2]
        gaps = [y[0]-x[0] for x, y in zip(currage[:-1], currage[1:])]
        delta = min(gaps)
        current = currage[-1]
        for iteration in range(7):
            expected = current[0] - delta
            matches = [x for x in currage if abs(x[0]-expected) < 7]
            if len(matches) == 0:
                current = (current[0]-delta, current[1]-delta, 0, 0)
                batches.append(current)
            else:
                current = matches[0]
        batches.sort()

    if len(batches) != 10:
        print(batches)
        raise Exception("Unexpected bars")

    agepct = [x[3]-x[2] for x in batches[:8]]
    agepct = [x/sum(agepct)*100 for x in agepct]
    genderpct = [x[3]-x[2] for x in batches[8:]]
    genderpct = [x/sum(genderpct)*100 for x in genderpct]

    # Output
    allage = ["0_19", "20_29", "30_39", "40_49", "50_59", "60_69", "70_79", "80_plus"]
    for val, age in zip(agepct, allage):
        out["Pct" + prefix + "Age_" + age] = round(val, 1)
    out["Pct" + prefix + "Female"] = round(genderpct[0], 1)
    out["Pct" + prefix + "Male"] = round(genderpct[1], 1)

def get_race_ethn_deaths(tab, out, driver):
    # Race + ethn table 
    r_head = driver.find_elements_by_xpath('//*[@id="demographics-charts-tabpane-demographics-deaths"]/div[2]/div[2]/div[1]/table/thead/tr/*')
    r_rows = driver.find_elements_by_xpath('//*[@id="demographics-charts-tabpane-demographics-deaths"]/div[2]/div[2]/div[1]/table/tbody/*')
    
    e_head = driver.find_elements_by_xpath('//*[@id="demographics-charts-tabpane-demographics-deaths"]/div[2]/div[2]/div[2]/table/thead/tr/*')
    e_rows = driver.find_elements_by_xpath('//*[@id="demographics-charts-tabpane-demographics-deaths"]/div[2]/div[2]/div[2]/table/tbody/*')

    # Get headers
    exp_headers = ["Race", "% of Deaths", "% of Indiana Population"]
    # print([x.text for x in r_head])
    for head in r_head:
        if head.text not in exp_headers:
            raise Exception("Unexpected header in race table " + head.text)

    exp_races = ["White", "Black or African American", "Other Race", "Asian", "Unknown"]
    # Get values
    for row in r_rows:
        vals = row.find_elements_by_xpath('.//*')
        if vals[0].text not in exp_races:
            raise Exception("Unexpected race "+ vals[0].text)
        if vals[0].text == "Unknown":
            if len(vals) != 3:
                raise Exception("Unexpected Row structure in table")
            out[tab + "Unknown Race"] = (vals[1].text).strip('%')
        elif vals[0].text == "Other Race":
            if len(vals) != 4:
                raise Exception("Check other race div")
            out[tab + vals[0].text] = (vals[2].text).strip('%')
        else:
            if len(vals) != 3:
                raise Exception("Unexpected Row structure in table")
            out[tab + vals[0].text] = (vals[1].text).strip('%')

    # Get headers
    exp_headers = ["Ethnicity", "% of Deaths", "% of Indiana Population"]
    for head in e_head:
        if head.text not in exp_headers:
            raise Exception("Unexpected header in ethn table " + head.text)
    
    # Get values
    exp_ethn = ['Not Hispanic or Latino', 'Hispanic or Latino', 'Unknown']
    for row in e_rows:
        vals = row.find_elements_by_xpath('.//*')
        if len(vals) != 3:
            raise Exception("Unexpected Row structure in table")
        if vals[0].text not in exp_ethn:
            raise Exception("Unexpected ethn "+ vals[0].text)
        if vals[0].text == "Unknown":
            out[tab + "Unknown Ethnicity"] = (vals[1].text).strip('%')
        else:
            out[tab + vals[0].text] = (vals[1].text).strip('%')
    return out

def get_race_ethn_cases(tab, out, driver):
    # Race + ethn table 
    r_head = driver.find_elements_by_xpath('//*[@id="demographics-charts-tabpane-demographics-cases"]/div[2]/div[2]/div[1]/table/thead/tr/*')
    r_rows = driver.find_elements_by_xpath('//*[@id="demographics-charts-tabpane-demographics-cases"]/div[2]/div[2]/div[1]/table/tbody/*')
    
    e_head = driver.find_elements_by_xpath('//*[@id="demographics-charts-tabpane-demographics-cases"]/div[2]/div[2]/div[2]/table/thead/tr/*')
    e_rows = driver.find_elements_by_xpath('//*[@id="demographics-charts-tabpane-demographics-cases"]/div[2]/div[2]/div[2]/table/tbody/*')
    
    # Get headers
    exp_headers = ["Race", "% of Cases", "% of Indiana Population"]
    for head in r_head:
        if head.text not in exp_headers:
            raise Exception("Unexpected header in race table " + head.text)

    exp_races = ["White", "Black or African American", "Other Race", "Asian", "Unknown"]
    # Get values
    for row in r_rows:
        vals = row.find_elements_by_xpath('.//*')
        if vals[0].text not in exp_races:
            raise Exception("Unexpected race "+ vals[0].text)
        if vals[0].text == "Unknown":
            if len(vals) != 3:
                raise Exception("Unexpected Row structure in table")
            out[tab + "Unknown Race"] = (vals[1].text).strip('%')
        elif vals[0].text == "Other Race":
            if len(vals) != 4:
                raise Exception("Check other race div")
            out[tab + vals[0].text] = (vals[2].text).strip('%')
        else:
            if len(vals) != 3:
                raise Exception("Unexpected Row structure in table")
            out[tab + vals[0].text] = (vals[1].text).strip('%')

    # Get headers
    exp_headers = ["Ethnicity", "% of Cases", "% of Indiana Population"]
    for head in e_head:
        if head.text not in exp_headers:
            raise Exception("Unexpected header in ethn table " + head.text)
    
    # Get values
    exp_ethn = ['Not Hispanic or Latino', 'Hispanic or Latino', 'Unknown']
    for row in e_rows:
        vals = row.find_elements_by_xpath('.//*')
        if vals[0].text not in exp_ethn:
            raise Exception("Unexpected ethn "+ vals[0].text)
        if vals[0].text == "Unknown":
            out[tab + "Unknown Ethnicity"] = (vals[1].text).strip('%')
        else:
            out[tab + vals[0].text] = (vals[1].text).strip('%')
    return out

def run_IN(args):
    # Parameters
    raw_name = '../IN/raw'
    data_name = '../IN/data/data.csv'
    now = str(datetime.now())

    out = {}
    baseurl = "https://coronavirus.in.gov/images/%s-demographics.jpg"
    caseImg = grabImg(baseurl % "positive", "%s/Case_%s.png" % (raw_name, now))
    grabData(caseImg, "Case", out)
    deathImg = grabImg(baseurl % "death", "%s/Death_%s.png" % (raw_name, now))
    grabData(deathImg, "Death", out)

     # Get Raw HTML
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    reg_url = "https://coronavirus.in.gov"
    req = Request(url=reg_url, headers=headers) 
    html = urlopen(req).read() 
    soup = BeautifulSoup(html, "html.parser")
    g = open('{}/{}.html'.format(raw_name, now), 'w')
    g.write(str(soup))
    g.close()

    # Selenium
    # Using Selenium
    # driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get("https://coronavirus.in.gov")
    time.sleep(5)
    driver.find_element_by_xpath('//*[@id="prefix-dismissButton"]').click()
    time.sleep(2)
    frame = driver.find_element_by_xpath('//*[@id="map-frame"]')
    driver.switch_to.frame(frame)
    time.sleep(5)

    # Get Race Data
    
    # Cases 
    out = get_race_ethn_cases("% Cases Race/Ethnicity: ", out, driver)
    # Deaths
    driver.find_element_by_xpath('//*[@id="demographics-charts-tab-demographics-deaths"]').click()
    time.sleep(2)
    out = get_race_ethn_deaths("% Deaths Race/Ethnicity: ", out, driver)
    # # Tested
    # driver.find_element_by_xpath('//*[@id="demographics-charts-tab-demographics-tested"]').click()
    # time.sleep(5)
    # out = get_race_ethn("% Tested Race/Ethnicity: ", out, driver)
    
    # Output
    out["Scrape_Time"] = now
    fields = sorted([x for x in out])
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])

if __name__ == '__main__':
    run_IN({})
