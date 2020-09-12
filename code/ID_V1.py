from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys
from urllib.request import urlopen
import os

def run_ID(args):
    # Parameters
    raw_name = '../ID/raw'
    data_name = '../ID/data/data.csv'

    # Open file
    exists = os.path.exists(data_name)
    f = open(data_name, 'a')
    writer = csv.writer(f)
    if not exists:
        writer.writerow(["Age [0-17]", "Age [18-49]", "Age [50+]", "Age [Unknown]", "Female", "Male", "Unknown Gender",
                         "Total Hospitalizations", "Total ICU Admissions", "Healthcare Workers with COVID-19", "pullTime"])

    # Scrape data
    now = datetime.now()
    html = urlopen("https://coronavirus.idaho.gov/").read()
    soup = BeautifulSoup(html, "html.parser")
    g = open('{}/{}.html'.format(raw_name, now), 'w')
    g.write(str(soup))
    g.close()

    # Get age distribution
    age1 = int(list(list(soup(text="<18 years")[0].parent.parent.children)[2].children)[0])
    age2 = int(list(list(soup(text=re.compile("18.49"))[0].parent.parent.children)[2].children)[0])
    age3 = int(list(list(soup(text="50+")[0].parent.parent.children)[2].children)[0])
    age4 = int(list(list(soup(text="Unknown")[0].parent.parent.children)[2].children)[0])

    # Get gender distribution
    female = int(list(list(soup(text="Female")[0].parent.parent.children)[2].children)[0])
    male = int(list(list(soup(text="Male")[0].parent.parent.children)[2].children)[0])
    unknown = int(list(list(soup(text="Unknown")[1].parent.parent.children)[2].children)[0])

    # Get reported hospitalizations for positive cases
    hosp1 = int(list(list(soup(text="Total Hospitalizations")[0].parent.parent.children)[2].children)[0])
    hosp2 = int(list(list(soup(text="Total ICU Admissions")[0].parent.parent.children)[2].children)[0])
    hosp3 = int(list(list(soup(text="Total Healthcare Workers with COVID-19")[0].parent.parent.children)[2].children)[0])
    
    # Write row
    writer.writerow([age1, age2, age3, age4, female, male, unknown, hosp1, hosp2, hosp3, now])

    # Close file
    f.close()

if __name__ == '__main__':
    run_ID({})
