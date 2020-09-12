from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys
import pdb
import numpy as np
import os
from urllib.request import urlopen

# Raises AttributeError or NotImplementedError
def getTime(txt):
    m = re.search('as of ([0-9]*) ([p,a]\.m\.) (PDT|Pacific Daylight Time)[ on ]*([A-Z][a-z]* [0-9]+)[\.,\,]', txt).groups()
    time = m[0] + m[1]
    tz = m[2]
    date = m[3]
    return date, time, tz

def month_first_time(txt):
    m = re.search('[a,A]s of ([A-Z][a-z]* [0-9]+), [0-9]+, ([0-9]+ [a,p]\.m\.) (PDT|Pacific Daylight Time),', txt).groups()
    time = m[1] 
    tz = m[2]
    date = m[0]
    return date, time, tz


stoi = lambda x: int(x.replace(",", ""))
def getCases(txt):
    txt = txt.replace("\xa0", " ")
    m = re.search(".([0-9,]+) – Positive cases", txt).groups()
    pos_cases = stoi(m[0])
    m = re.search("([0-9,]+) – Deaths", txt).groups()
    deaths = stoi(m[0])
    # Gender 
    m = re.search("Gender of all", txt)
    if m is None: 
        f_cases = np.nan
        m_cases = np.nan
        u_cases = np.nan
        gender_ind = len(txt)
    else: 
        gender_ind = m.span()[1]
        subtxt = txt[gender_ind:]
        m = re.search("Female: ([0-9,]+) cases", subtxt).groups()
        f_cases = stoi(m[0])
        m = re.search("Male: ([0-9,]+)", subtxt).groups()
        m_cases = stoi(m[0])
        m = re.search("Unknown: ([0-9,]+)", subtxt).groups()
        u_cases = stoi(m[0])
    # Age
    m = re.search("Ages of all", txt)
    if m is None: 
        a17 = np.nan
        au = np.nan
    else:
        age_ind = m.span()[1]
        subtxt = txt[age_ind: gender_ind]
        a17 = stoi(re.search("Age 0-17:[ ]+([0-9,]+)", subtxt).groups()[0])
        au = stoi(re.search("Unknown: ([0-9,]+)", subtxt).groups()[0])
        m = re.search("Age 18-49: ([0-9,]+)", subtxt)
        a1849 = stoi(m.groups()[0]) if m is not None else np.nan
        m = re.search("Age 50-64: ([0-9,]+)", subtxt)
        a5064 = stoi(m.groups()[0]) if m is not None else np.nan
        a65 = stoi(re.search("Age 65+.. ([0-9,]+)", subtxt).groups()[0])
        m = re.search("Age 18-64: ([0-9,]+)", subtxt)
        a1864 = stoi(m.groups()[0]) if m is not None else a1849+a5064
    return pos_cases, deaths, f_cases, m_cases, u_cases, a17, a1849, a5064, a1864,a65, au

def getTests(txt):
    m = re.search("Testing in California",txt)
    if m is None: 
        tests = np.nan
    else:
        subtxt = txt[m.span()[1]:]
        tests = stoi(re.search("approximately ([0-9,]+)", subtxt).groups()[0])
        m = re.search("At least ([0-9,\,]+) results have been received and another ([0-9,\,]+) are pending.", subtxt)
        test_res = stoi(m.groups()[0]) if m is not None else np.nan
        test_pending = stoi(m.groups()[1]) if m is not None else np.nan
    return tests, test_res, test_pending

def run_CA(args):
    raw_name = '../CA/raw'
    data_name = '../CA/data/data.csv'    
    
    scraped = []
    exists = os.path.exists(data_name)
    if exists:
        fp = open(data_name)
        reader = csv.reader(fp, delimiter=",")
        for row in reader:
            scraped.append(row)
        fp.close()
    visited_links = [i[-2] for i in scraped]
    fp = open(data_name, 'w')
    writer = csv.writer(fp)
    if exists:
        writer.writerow(scraped[0])
        scraped = scraped[1:]
    if not scraped:
        writer.writerow(["state", "stateAbbrev", "date", "time", "tz", "fatalities", "cases", "female_case",
                         "male_cases", "unkown_gender_c", "age0_17", "age18_49", "age50_64", "age18_64", "age65", "unkown_age", 
                         "tot_tests", "tests_with_results", "tests_pending", "link", "scrape_time"])

    #html = urlopen("https://www.cdph.ca.gov/Programs/CID/DCDC/Pages/Immunization/ncov2019.aspx").read()
    #soup = BeautifulSoup(html, "html.parser")
    #soup = soup.find_all("div", class_="ms-rtestate-field")[1]
    #soup.find(text="COVID-19 by the Numbers").parent.parent.find_next("p")
    #txt = soup.find(text="COVID-19 by the Numbers").parent.parent.find_next("p").text
    #date, time, tz = month_first_time(txt)
    #txt = soup.find(text="COVID-19 by the Numbers").parent.parent.find_next("p").text



    base = "https://www.cdph.ca.gov"
    html = urlopen(f"{base}/Programs/OPA/Pages/New-Release-2020.aspx").read()
    soup = BeautifulSoup(html, "html.parser")

    emergency_file = "State Health & Emergency Officials[\xa0, ]Announce Latest COVID-19 Facts"
    for x in soup.find_all("th", {'class':["ms-rteTableFirstCol-default", "ms-rteTableHeaderFirstCol-default"]}):
        # Find link to visit
        link = [a["href"] for a in x.find_all('a', href=True)][0]
        link = link if link.startswith("https") else f"{base}{link}"
        if link in visited_links:
            break

        # Now go there 
        html = urlopen(link).read()
        subsoup = BeautifulSoup(html, "html.parser")

        val = link.split('/')[-1].split('.')[0]
        g = open('{}/{}.html'.format(raw_name, val), 'w')
        g.write(str(subsoup))
        g.close()

        # Detect what type of file it is
        # get date
        txt = subsoup("div", class_="NewsItemContent")[1].text
        if re.search(emergency_file, txt) is not None:
            for y in subsoup.find_all("strong"):
                if y.text.startswith("COVID-19 in California by the Numbers"):
                    day, time, tz = getTime(y.parent.text.replace("\xa0", " "))
                    pos, death, fc, mc, uc, a17, a1849, a5064, a1864, a65, au= getCases(y.parent.parent.text.replace("\xa0", " "))
                    tests = np.nan
        else:
            m = re.search("The following.*Testing in California",subsoup.text)
            if m is None:
                txt = subsoup.text.replace("\xa0", " ")
                m = re.search("COVID-19 in California by the Numbers.*How People", txt)
                if m is None:
                    raise NotImplementedError
            day, time, tz = getTime(m.group())
            pos, death, fc, mc, uc, a17, a1849, a5064, a1864, a65, au= getCases(m.group())
            tests, testRes, testPend = getTests(subsoup.text)
        now = datetime.now()
        writer.writerow(["California", "CA", day, time, "PDT", death, pos, fc, mc, uc,
                         a17, a1849, a5064, a1864, a65, au, tests, testRes, testPend,
                         link, now])

    for row in scraped:
        writer.writerow(row)

    fp.close()

if __name__ == '__main__':
    run_CA({})
