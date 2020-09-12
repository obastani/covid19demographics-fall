from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys
from urllib.request import urlopen, Request
import os

def run_DC(args):
    # Parameters
    raw_name = '../DC/raw'
    data_name = '../DC/data/data.csv'

    # Open file
    exists = os.path.exists(data_name)
    f = open(data_name, 'a')
    writer = csv.writer(f)
    if not exists:
        writer.writerow(["Age [0-18]: Female Cases", "Age [19-30]: Female Cases", "Age [31-40]: Female Cases", "Age [41-50]: Female Cases",
                         "Age [51-60]: Female Cases", "Age [61-70]: Female Cases", "Age [71-80]: Female Cases", "Age [81+]: Female Cases",
                         "Age [0-18]: Male Cases", "Age [19-30]: Male Cases", "Age [31-40]: Male Cases", "Age [41-50]: Male Cases",
                         "Age [51-60]: Male Cases", "Age [61-70]: Male Cases", "Age [71-80]: Male Cases", "Age [81+]: Male Cases",
                         "pullTime"])

    # Scrape demographic data
    now = datetime.now()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    reg_url = 'https://coronavirus.dc.gov/page/coronavirus-data'
    req = Request(url=reg_url, headers=headers) 
    html = urlopen(req).read() 
    soup = BeautifulSoup(html, "html.parser")
    g = open('{}/{}.html'.format(raw_name, now), 'w')
    g.write(str(soup))
    g.close()

    # Get demographic data
    agef1 = int(list(list(list(soup(text='0-18')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    agef2 = int(list(list(list(soup(text='19-30')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    agef3 = int(list(list(list(soup(text='31-40')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    agef4 = int(list(list(list(soup(text='41-50')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    agef5 = int(list(list(list(soup(text='51-60')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    agef6 = int(list(list(list(soup(text='61-70')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    agef7 = int(list(list(list(soup(text='71-80')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])
    agef8 = int(list(list(list(soup(text='81+')[0].parent.parent.parent.parent.children)[5].children)[1].children)[0])

    agem1 = int(list(list(list(soup(text='0-18')[0].parent.parent.parent.parent.children)[7].children)[1].children)[0])
    agem2 = int(list(list(list(soup(text='19-30')[0].parent.parent.parent.parent.children)[7].children)[1].children)[0])
    agem3 = int(list(list(list(soup(text='31-40')[0].parent.parent.parent.parent.children)[7].children)[1].children)[0])
    agem4 = int(list(list(list(soup(text='41-50')[0].parent.parent.parent.parent.children)[7].children)[1].children)[0])
    agem5 = int(list(list(list(soup(text='51-60')[0].parent.parent.parent.parent.children)[7].children)[1].children)[0])
    agem6 = int(list(list(list(soup(text='61-70')[0].parent.parent.parent.parent.children)[7].children)[1].children)[0])
    agem7 = int(list(list(list(soup(text='71-80')[0].parent.parent.parent.parent.children)[7].children)[1].children)[0])
    agem8 = int(list(list(list(soup(text='81+')[0].parent.parent.parent.parent.children)[7].children)[1].children)[0])

    # Write row
    writer.writerow([agef1, agef2, agef3, agef4, agef5, agef6, agef7, agef8,
                     agem1, agem2, agem3, agem4, agem5, agem6, agem7, agem8, now])

    # Close file
    f.close()

if __name__ == '__main__':
    run_DC({})
