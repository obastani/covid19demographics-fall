# curl https://apps.health.tn.gov/AEM_embed/TDH-2019-Novel-Coronavirus-Epi-and-Surveillance.pdf > 4-12-20.pdf

from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys
from urllib.request import urlopen, Request
import os
# import tabula
import requests

def get_raw(raw_name):
    # Scrape data
    now = datetime.now()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    reg_url = 'https://www.tn.gov/health/cedep/ncov/data.html'
    req = Request(url=reg_url, headers=headers) 
    html = urlopen(req).read() 
    soup = BeautifulSoup(html, "html.parser")
    g = open('{}/{}.html'.format(raw_name, now), 'w')
    g.write(str(soup))
    g.close()

    # Get pdf link
    pdf_link = soup.find("iframe")['src']
    
    # Save pdf to raw
    try:
        r = requests.get(pdf_link)
    except:
        print("Unable to open PDF from link")
        raise
    
    with open ('{}/{}.pdf'.format(raw_name, now), "wb") as pdf:
        pdf.write(r.content)


def run_TN(args):
    # Parameters
    broken = True
    raw_name = '../TN/raw'
    data_name = '../TN/data/data.csv'

    if broken:
        get_raw(raw_name)
    
    # Exiting after getting raw data
    '''
    exit()

    # Open file
    exists = os.path.exists(data_name)
    f = open(data_name, 'a')
    writer = csv.writer(f)
    if not exists:
        writer.writerow(["Age [0-10]: Cases", "Age [11-20]: Cases", "Age [21-30]: Cases", "Age [31-40]: Cases", "Age [41-50]: Cases",
                         "Age [51-60]: Cases", "Age [61-70]: Cases", "Age [71-80]: Cases", "Age [80+]: Cases", "Age [pending]: Cases",
                         "Age [0-10]: Deaths", "Age [11-20]: Deaths", "Age [21-30]: Deaths", "Age [31-40]: Deaths", "Age [41-50]: Deaths",
                         "Age [51-60]: Deaths", "Age [61-70]: Deaths", "Age [71-80]: Deaths", "Age [80+]: Deaths", "Age [pending]: Deaths",
                         "Race: White", "Race: Black", "Race: Other", "Race: Asian", "Race: pending", "Gender: Female", "Gender: Male", "Gender: pending",
                         "Hospitalizations","pullTime"])

    # Scrape data
    now = datetime.now()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    reg_url = 'https://www.tn.gov/health/cedep/ncov.html'
    req = Request(url=reg_url, headers=headers) 
    html = urlopen(req).read() 
    soup = BeautifulSoup(html, "html.parser")
    g = open('{}/{}.html'.format(raw_name, now), 'w')
    g.write(str(soup))
    g.close()

    # Get age distribution
    age1c = int(list(list(list(soup(text='0-10')[0].parent.parent.parent.children)[2].children)[0].children)[0])
    age2c = int(list(list(list(soup(text='11-20')[0].parent.parent.parent.children)[2].children)[0].children)[0])
    age3c = int(list(list(list(soup(text='21-30')[0].parent.parent.parent.children)[2].children)[0].children)[0])
    age4c = int(list(list(list(soup(text='31-40')[0].parent.parent.parent.children)[2].children)[0].children)[0])
    age5c = int(list(list(list(soup(text='41-50')[0].parent.parent.parent.children)[2].children)[0].children)[0])
    age6c = int(list(list(list(soup(text='51-60')[0].parent.parent.parent.children)[2].children)[0].children)[0])
    age7c = int(list(list(list(soup(text='61-70')[0].parent.parent.parent.children)[2].children)[0].children)[0])
    age8c = int(list(list(list(soup(text='71-80')[0].parent.parent.parent.children)[2].children)[0].children)[0])
    age9c = int(list(list(list(soup(text='81+')[0].parent.parent.parent.children)[2].children)[0].children)[0])
    age10c = int(list(list(list(soup(text='PENDING')[0].parent.parent.parent.children)[2].children)[0].children)[0])

    age1d = int(list(list(list(soup(text='0-10')[0].parent.parent.parent.children)[4].children)[0].children)[0])
    age2d = int(list(list(list(soup(text='11-20')[0].parent.parent.parent.children)[4].children)[0].children)[0])
    age3d = int(list(list(list(soup(text='21-30')[0].parent.parent.parent.children)[4].children)[0].children)[0])
    age4d = int(list(list(list(soup(text='31-40')[0].parent.parent.parent.children)[4].children)[0].children)[0])
    age5d = int(list(list(list(soup(text='41-50')[0].parent.parent.parent.children)[4].children)[0].children)[0])
    age6d = int(list(list(list(soup(text='51-60')[0].parent.parent.parent.children)[4].children)[0].children)[0])
    age7d = int(list(list(list(soup(text='61-70')[0].parent.parent.parent.children)[4].children)[0].children)[0])
    age8d = int(list(list(list(soup(text='71-80')[0].parent.parent.parent.children)[4].children)[0].children)[0])
    age9d = int(list(list(list(soup(text='81+')[0].parent.parent.parent.children)[4].children)[0].children)[0])
    age10d = int(list(list(list(soup(text='PENDING')[0].parent.parent.parent.children)[4].children)[0].children)[0])

    # Get race distribution
    white = int(list(list(list(soup(text='White')[0].parent.parent.parent.children)[2].children)[0].children)[0].replace(',',''))
    black = int(list(list(list(soup(text='Black or African American')[0].parent.parent.parent.children)[2].children)[0].children)[0].replace(',',''))
    other = int(list(list(list(soup(text='Other/ Multiracial')[0].parent.parent.parent.children)[2].children)[0].children)[0].replace(',',''))
    asian = int(list(list(list(soup(text='Asian')[0].parent.parent.parent.children)[2].children)[0].children)[0].replace(',',''))
    pending = int(list(list(list(soup(text='Pending')[0].parent.parent.parent.children)[2].children)[0].children)[0].replace(',',''))

    # Get gender distribution
    female = int(list(list(list(soup(text='Female')[0].parent.parent.parent.children)[2].children)[0].children)[0].replace(',',''))
    male = int(list(list(list(soup(text='Male')[0].parent.parent.parent.children)[2].children)[0].children)[0].replace(',',''))
    gender = int(list(list(list(soup(text='Pending')[2].parent.parent.parent.children)[2].children)[0].children)[0].replace(',',''))
    
    # Get hospitalizations and fatalities
    hosp = int(list(list(soup(text='Hospitalizations')[0].parent.parent.children)[2].children)[0])
    
    # Write row
    writer.writerow([age1c, age2c, age3c, age4c, age5c, age6c, age7c, age8c, age9c, age10c,
                     age1d, age2d, age3d, age4d, age5d, age6d, age7d, age8d, age9d, age10d,
                     white, black, other, asian, pending, female, male, gender, hosp, now])

    # Close file
    f.close()
    '''

if __name__ == '__main__':
    run_TN({})
