from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys
from urllib.request import urlopen
import os

def run_GU(args):
    # Parameters
    raw_name = '../GU/raw'

    # Scrape HTML
    html = urlopen("https://ghs.guam.gov/coronavirus-covid-19?page0").read()
    soup = BeautifulSoup(html, "html.parser")

    # Get buttons
    buttons = soup('button', text='MORE INFO')
    for button in buttons:
        # Get index
        try:
            index = int(button.parent['href'].split('-')[3])
        except:
            continue

        # Scrape button HTML
        html_button = urlopen('https://ghs.guam.gov' + button.parent['href'])
        soup_button = BeautifulSoup(html_button, "html.parser")

        # Write HTML
        f = open('{}/{}.html'.format(raw_name, index), 'w')
        f.write(str(soup_button))
        f.close()

        break

if __name__ == '__main__':
    run_GU({})
