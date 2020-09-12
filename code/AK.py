from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
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
import requests

def get_historical():
    months = ["apr", "may", "jun", "jul"]
    days = [str(x) for x in range(32) if x != 0]
    single_dig = [str(x) for x in range(10)]

    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()

    for month in months:
        for day in days:
            if day in single_dig:
                day = "0" + day
            base_url = "https://coronavirus-response-alaska-dhss.hub.arcgis.com/datasets/summary-tables-"
            date = day + month + "2020"
            url = base_url + date
            try:
                driver.get(url)
                time.sleep(5)
                driver.find_element_by_xpath('//*[@id="simple-download-button"]').click()
                time.sleep(2)
            except:
                print("Could not find summary table for " + date)
    
def get_summary(url, raw_name, str_date):
    # We want to get the link of the download button
    href = ""
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    # Try to get href
    try:
        driver.get(url)
        time.sleep(5)
        download_button = driver.find_element_by_xpath('//*[@id="simple-download-button"]')
        href = download_button.get_attribute("href")
    except:
        print("Unable to get download link")
        raise
    # Using href, download to raw folder
    r = requests.get(href, allow_redirects=True)
    with open(raw_name + "/Summary_Tables_(" + str_date + ").xlsx", "wb") as f:
        f.write(r.content)

def run_AK(args):
    # Parameters
    raw_name = '../AK/raw'
    # data_name = '../AK/data/data.csv'
    hist = False
    now = str(datetime.now())

    if hist:
        get_historical()
    else:
        get_summary('https://coronavirus-response-alaska-dhss.hub.arcgis.com/datasets/summary-tables', raw_name, now)
        # base_url = "https://coronavirus-response-alaska-dhss.hub.arcgis.com/datasets/summary-tables-"
        # today = datetime.now()
        # str_date = today.strftime("%d%b%Y").lower()
        # all_dates = []
        # scrape = True
        # for file in os.listdir(raw_name):
        #     hist_date = ((((file.replace("Summary_Tables_(","")).replace(").xlsx", "")).replace(")_(2", "")).replace("-2","")).replace("~$", "").lower()
        #     all_dates.append(hist_date)
        
        # # Finding most recent collected date
        # not_found = True
        # most_recent = None
        # # Checks if today was already scraped
        # if str_date in all_dates:
        #     scrape = False
        # else:

        #     d = today
        #     # Will keep iterating through directory to find most recent by decrementing
        #     while not_found:
        #         # Decrements
        #         d = d - timedelta(days=1)
        #         # Creates string for comparison
        #         str_d = d.strftime("%d%b%Y").lower()
        #         # If in list, then becomes most recent
        #         if str_d in all_dates:
        #             not_found = False
        #             most_recent = d + timedelta(days=1)
        #             str_date = most_recent.strftime("%d%b%Y").lower()
        
        # print(today)
        # print(most_recent)
        # print((today - most_recent).days)

        # exit()

        # if scrape:
        #     # If difference of today and most recent, we will try to grab all the raw
        #     if (today - most_recent).days > 0:
        #         # Until most recent is tomorrow
        #         while most_recent != (today + timedelta(days=1)):
        #             # Get current date, convert to string
        #             cur_date = most_recent.strftime("%d%b%Y").lower()
        #             # Call function
        #             get_summary(base_url + cur_date, raw_name, cur_date)
        #             # Increment most_recent
        #             most_recent = most_recent + timedelta(days=1)
        #     else:
        #         # This means today is the most recent, simply try to grab the data
        #         get_summary(base_url + str_date, raw_name, str_date)

            

            

if __name__ == '__main__':
    run_AK({})