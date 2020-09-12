import os
import csv
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_ICE():
    # Parameters
    raw_name = "../Iceland/raw"
    data_name = "../Iceland/data/data.csv"
    url = "https://www.worldometers.info/coronavirus/"
    now = str(datetime.now())
    page = requests.get(url)

    # Beautiful Soup
    soup = BeautifulSoup(page.content,'html.parser')

    # Write to raw file
    with open("%s/%s.html" % (raw_name, now), "w") as fp:
        fp.write(str(soup))

    # Expected Headers
    exp_headers = ['#', 'Country,Other', 'TotalCases', 'NewCases', 'TotalDeaths',
                   'NewDeaths', 'TotalRecovered', 'NewRecovered', 'ActiveCases',
                   'Serious,Critical', 'Tot\xa0Cases/1M pop', 'Deaths/1M pop',
                   'TotalTests', 'Tests/\n1M pop\n', 'Population', 'Continent', 
                   '1 Caseevery X ppl', '1 Deathevery X ppl', '1 Testevery X ppl']

    # Getting Headers
    table_columns = (soup.find("thead")).findAll("th")

    # Check headers are in the same tag
    if table_columns == None:
        raise Exception("Could not find table fields")

    # Getting current header/column names of the table
    cur_headers = []
    for idx in range(len(table_columns)):
        cur_headers.append(table_columns[idx].get_text())
    
    # Checking column names and order are the same as expected
    for cur_header in cur_headers:
        if cur_header not in exp_headers:
            raise Exception("Unexpected Column name: " + cur_header)
        if exp_headers.index(cur_header) != cur_headers.index(cur_header):
            raise Exception("Unexpected Order of Column name")
    
    # Checking number of columns are the same
    if len(cur_headers) != len(exp_headers):
        raise Exception("Unexpected number of columns")

    # Finding Icelandd <a> to get parent
    a_tag = soup.find("a", {"href": "country/iceland/"})
    # Check if the find returns none
    if a_tag == None:
        raise Exception("Unable to find <a> for Iceland")
    # Gets Iceland Row
    row = (a_tag.parent).parent
    
    # Finds all td tags that contain all the col values
    td_tags = row.findAll("td")
    values = []
    # Checking we are getting the expected number of values
    if len(cur_headers) != len(td_tags):
        raise Exception("Unexpected number of values in row")
    
    # Stringifying values inside tags
    for idx in range(len(td_tags)):
        values.append(td_tags[idx].get_text())

    # Creating out dictionary with values from values[]
    out = {
        "Date": now,
        "Total_Cases": int(values[2].replace(",","")),
        "Active_Cases": int(values[8].replace(",","")),
        "Total_Deaths": int(values[4].replace(",",""))
    }
    
    # Write to file
    exists = os.path.exists(data_name)
    fields = [x for x in out]
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])

def run_Iceland(args):
    scrape = True
    if scrape:
        scrape_ICE()
    
if __name__ == '__main__':
    run_Iceland({})
