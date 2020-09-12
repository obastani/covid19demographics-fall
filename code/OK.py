from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys
import urllib
from urllib.request import urlopen
import requests
import os
import ssl

def run_OK(args):
    # Parameters
    raw_name = '../OK/raw'
    now = str(datetime.now())

    # Get PDF automatically 
    r = requests.get('https://storage.googleapis.com/ok-covid-gcs-public-download/covid19_cases_summary.pdf')

    with open(raw_name + "/" + now + ".pdf", 'wb') as f:
        f.write(r.content)

    # data_name = '../OK/data/data.csv'

    # # Open file
    # exists = os.path.exists(data_name)
    # f = open(data_name, 'a')
    # writer = csv.writer(f)
    # if not exists:
    #     writer.writerow(["Age [0-4]", "Age [5-17]", "Age [18-35]", "Age [36-49]", "Age [50-64]", "Age [65+]",
    #                      "Female", "Male", "Total", "pullTime"])

    # ctx = ssl.create_default_context()
    # ctx.check_hostname = False
    # ctx.verify_mode = ssl.CERT_NONE

    # # Scrape data
    # now = datetime.now()

    # user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    # headers = { 'User-Agent' : user_agent }
    # req = urllib.request.Request("https://coronavirus.health.ok.gov", headers=headers)

    # #html = urlopen("https://coronavirus.health.ok.gov", context=ctx).read()
    # html = urlopen(req, context=ctx).read()
    # soup = BeautifulSoup(html, "html.parser")
    # g = open('{}/{}.html'.format(raw_name, now), 'w')
    # g.write(str(soup))
    # g.close()

    # # Get total
    # total = int(list(list(soup(text='Total')[0].parent.parent.children)[3].children)[0].replace(',', ''))

    # # Get age distribution
    # age1 = int(list(list(soup(text='00-04')[0].parent.parent.children)[3].children)[0].replace(',', ''))
    # age2 = int(list(list(soup(text='05-17')[0].parent.parent.children)[3].children)[0].replace(',', ''))
    # age3 = int(list(list(soup(text='18-35')[0].parent.parent.children)[3].children)[0].replace(',', ''))
    # age4 = int(list(list(soup(text='36-49')[0].parent.parent.children)[3].children)[0].replace(',', ''))
    # age5 = int(list(list(soup(text='50-64')[0].parent.parent.children)[3].children)[0].replace(',', ''))
    # age6 = int(list(list(soup(text='65+')[0].parent.parent.children)[3].children)[0].replace(',', ''))

    # # Get gender distribution
    # female = int(list(list(soup(text='Female')[0].parent.parent.children)[3].children)[0].replace(',', ''))
    # male = int(list(list(soup(text='Male')[0].parent.parent.children)[3].children)[0].replace(',', ''))
    
    # # Write row
    # writer.writerow([age1, age2, age3, age4, age5, age6, female, male, total, now])

    # # Close file
    # f.close()

if __name__ == '__main__':
    run_OK({})
