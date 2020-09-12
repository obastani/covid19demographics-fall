from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys
from urllib.request import urlopen, Request
import os

def run_OR(args):
    # Parameters
    raw_name = '../OR/raw'
    data_name = '../OR/data/data.csv'

    # Open file
    exists = os.path.exists(data_name)
    f = open(data_name, 'a')
    writer = csv.writer(f)
    if not exists:
        writer.writerow(["Cases: Age [0-9]", "Cases: Age [10-19]", "Cases: Age [20-29]", "Cases: Age [30-39]", "Cases: Age [40-49]", "Cases: Age [50-59]",
                         "Cases: Age [60-69]", "Cases: Age [70-79]", "Cases: Age [80+]", "Cases: Age [NA]}",
                         "Hospitalized: Age [0-9]", "Hospitalized: Age [10-19]", "Hospitalized: Age [20-29]",
                         "Hospitalized: Age [30-39]", "Hospitalized: Age [40-49]", "Hospitalized: Age [50-59]", "Hospitalized: Age [60-69]",
                         "Hospitalized: Age [70-79]", "Hospitalized: Age [80+]", "Hospitalized: Age [NA]}",
                         "Deaths: Age [0-9]", "Deaths: Age [10-19]", "Deaths: Age [20-29]",
                         "Deaths: Age [30-39]", "Deaths: Age [40-49]", "Deaths: Age [50-59]", "Deaths: Age [60-69]", "Deaths: Age [70-79]",
                         "Deaths: Age [80+]", "Deaths: Age [NA]}", "Cases: Female", "Cases: Male", "Cases: NA Gender", "Deaths: Female", "Deaths: Male",
                         "Deaths: NA Gender", "Hospitalized: yes", "Hospitalized: no", "Hospitalized: unknown", "Available Adult ICU Beds",
                         "Total ICU Beds","Available Adult non-ICU Beds", "Total Adult non-ICU Beds", "Available Pediatric NICU/PICU Beds",
                         "Total Pediatric NICU/PICU Beds", "Available Pediatric non-ICU Beds", "Total Pediatric non-ICU Beds", "Available Ventilators",
                         "Currently Hospitalized: COVID-19 Confirmed and Suspected", "Patients in ICU Beds: COVID-19 Confirmed and Suspected",
                         "Patients on Ventilators: COVID-19 Confirmed and Suspected", "Currently Hospitalized: COVID-19 Confirmed",
                         "Patients in ICU Beds: COVID-19 Confirmed", "Patients on Ventilators: COVID-19 Confirmed","pullTime"])

    # Scrape data
    now = datetime.now()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    reg_url = 'https://govstatus.egov.com/OR-OHA-COVID-19'
    req = Request(url=reg_url, headers=headers) 
    html = urlopen(req).read() 
    soup = BeautifulSoup(html, "html.parser")
    g = open('{}/{}.html'.format(raw_name, now), 'w')
    g.write(str(soup))
    g.close()

    # Get age distribution for cases
    age1c = int(list(list(soup(text='0 to 9')[0].parent.parent.children)[2].children)[0])
    age2c = int(list(list(soup(text='10 to 19')[0].parent.parent.children)[2].children)[0])
    age3c = int(list(list(soup(text='20 to 29')[0].parent.parent.children)[2].children)[0])
    age4c = int(list(list(soup(text='30 to 39')[0].parent.parent.children)[2].children)[0])
    age5c = int(list(list(soup(text='40 to 49')[0].parent.parent.children)[2].children)[0])
    age6c = int(list(list(soup(text='50 to 59')[0].parent.parent.children)[2].children)[0])
    age7c = int(list(list(soup(text='60 to 69')[0].parent.parent.children)[2].children)[0])
    age8c = int(list(list(soup(text='70 to 79')[0].parent.parent.children)[2].children)[0])
    age9c = int(list(list(soup(text='80 and over')[0].parent.parent.children)[2].children)[0])
    age10c = list(list(soup(text='Not available')[0].parent.parent.children)[2].children)[0]
    
    # Get age distribution for hospitalizations
    age1h = int(list(list(soup(text='0 to 9')[0].parent.parent.children)[6].children)[0])
    age2h = int(list(list(soup(text='10 to 19')[0].parent.parent.children)[6].children)[0])
    age3h = int(list(list(soup(text='20 to 29')[0].parent.parent.children)[6].children)[0])
    age4h = int(list(list(soup(text='30 to 39')[0].parent.parent.children)[6].children)[0])
    age5h = int(list(list(soup(text='40 to 49')[0].parent.parent.children)[6].children)[0])
    age6h = int(list(list(soup(text='50 to 59')[0].parent.parent.children)[6].children)[0])
    age7h = int(list(list(soup(text='60 to 69')[0].parent.parent.children)[6].children)[0])
    age8h = int(list(list(soup(text='70 to 79')[0].parent.parent.children)[6].children)[0])
    age9h = int(list(list(soup(text='80 and over')[0].parent.parent.children)[6].children)[0])
    age10h = list(list(soup(text='Not available')[0].parent.parent.children)[6].children)[0]
    
    # Get age distribution for deaths
    age1d = int(list(list(soup(text='0 to 9')[0].parent.parent.children)[8].children)[0])
    age2d = int(list(list(soup(text='10 to 19')[0].parent.parent.children)[8].children)[0])
    age3d = int(list(list(soup(text='20 to 29')[0].parent.parent.children)[8].children)[0])
    age4d = int(list(list(soup(text='30 to 39')[0].parent.parent.children)[8].children)[0])
    age5d = int(list(list(soup(text='40 to 49')[0].parent.parent.children)[8].children)[0])
    age6d = int(list(list(soup(text='50 to 59')[0].parent.parent.children)[8].children)[0])
    age7d = int(list(list(soup(text='60 to 69')[0].parent.parent.children)[8].children)[0])
    age8d = int(list(list(soup(text='70 to 79')[0].parent.parent.children)[8].children)[0])
    age9d = int(list(list(soup(text='80 and over')[0].parent.parent.children)[8].children)[0])
    age10d = list(list(soup(text='Not available')[0].parent.parent.children)[8].children)[0]
    
    # Get gender distribution for cases
    femalec = int(list(list(soup(text='Female')[0].parent.parent.children)[2].children)[0])
    malec = int(list(list(soup(text='Male')[0].parent.parent.children)[2].children)[0])
    gendernac = list(list(soup(text='Not available')[1].parent.parent.children)[2].children)[0]
    
    # Get gender distribution for deaths
    femaled = int(list(list(soup(text='Female')[0].parent.parent.children)[6].children)[0])
    maled = int(list(list(soup(text='Male')[0].parent.parent.children)[6].children)[0])
    gendernad = list(list(soup(text='Not available')[1].parent.parent.children)[6].children)[0]
    
    # Get hospitalizations
    hosp1 = int(list(list(soup(text='Yes')[0].parent.parent.children)[2].children)[0])
    hosp2 = int(list(list(soup(text='No')[0].parent.parent.children)[2].children)[0])
    hosp3 = int(list(list(soup(text='Not provided')[0].parent.parent.children)[2].children)[0])
    
    # Get hospital capacity info
    icu1 = int(list(list(soup(text='Adult ICU beds')[0].parent.parent.children)[2].children)[0])
    icu2 = int(list(list(soup(text='Adult ICU beds')[0].parent.parent.children)[4].children)[0])
    icu3 = int(list(list(soup(text= re.compile('Adult non-ICU.beds'))[0].parent.parent.children)[2].children)[0].replace(",", ""))
    icu4 = int(list(list(soup(text= re.compile('Adult non-ICU.beds'))[0].parent.parent.children)[4].children)[0].replace(",", ""))
    icu5 = int(list(list(soup(text='Pediatric NICU/PICU beds')[0].parent.parent.children)[2].children)[0])
    icu6 = int(list(list(soup(text='Pediatric NICU/PICU beds')[0].parent.parent.children)[4].children)[0])
    icu7 = int(list(list(soup(text='Pediatric non-ICU beds')[0].parent.parent.children)[2].children)[0])
    icu8 = int(list(list(soup(text='Pediatric non-ICU beds')[0].parent.parent.children)[4].children)[0])
    vent = int(list(list(soup(text='Ventilators')[0].parent.parent.children)[2].children)[0])
    admits1 = int(list(list(soup(text='Current hospitalized patients')[0].parent.parent.children)[2].children)[0])
    admits2 = int(list(list(soup(text='Current patients in ICU beds')[0].parent.parent.children)[2].children)[0])
    admits3 = int(list(list(soup(text='Current patients on ventilators')[0].parent.parent.children)[2].children)[0])
    admits4 = int(list(list(soup(text='Current hospitalized patients')[0].parent.parent.children)[4].children)[0])
    admits5 = int(list(list(soup(text='Current patients in ICU beds')[0].parent.parent.children)[4].children)[0])
    admits6 = int(list(list(soup(text='Current patients on ventilators')[0].parent.parent.children)[4].children)[0])

    # Write row
    writer.writerow([age1c, age2c, age3c, age4c, age5c, age6c, age7c, age8c, age9c, age10c,
                     age1h, age2h, age3h, age4h, age5h, age6h, age7h, age8h, age9h, age10h,
                     age1d, age2d, age3d, age4d, age5d, age6d, age7d, age8d, age9d, age10d,
                     femalec, malec, gendernac, femaled, maled, gendernad,
                     hosp1, hosp2, hosp3, icu1, icu2, icu3, icu4, icu5, icu6, icu7, icu8,
                     vent, admits1, admits2, admits3, admits4, admits5, admits6, now])

    # Close file
    f.close()

    # Get County Data - Andrew
    county_data_name = '../OR/data/data_county.csv'
    exp_headers = ['County', 'Cases1', 'Deaths2', 'Negatives3']
    headers = list(list(list(list(soup(text='County'))[0].parent.parent.parent.parent.children)[0].children)[0].children)
    while("\n" in headers):
        headers.remove("\n")
    if len(headers) != len(exp_headers):
        raise Exception("Unequal number of headers in county table")
    for i in range(len(headers)):
        if headers[i].text != exp_headers[i]:
            print(headers[i].text)
            raise Exception("Unexpected header in county table or unexpected order")
    counties = list(list(list(soup(text='County'))[0].parent.parent.parent.parent.children)[2].children)
    while("\n" in counties):
        counties.remove("\n")
    
    out_county = []
    for county in counties:
        row = list(county.children)
        while("\n" in row):
            row.remove("\n")
        if row[0].text != "Total":
            county_dict = {
                "County Name": row[0].text,
                "Total Cases": row[1].text,
                "Total Deaths": row[2].text,
                "Total Tested: Negative": row[3].text,
                "Scrape Time": now
            }
            out_county.append(county_dict)
    
    # Output - county
    for county in out_county:
        fields = sorted([x for x in county])
        exists = os.path.exists(county_data_name)
        with open(county_data_name, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([county[x] for x in fields])


if __name__ == '__main__':
    run_OR({})
