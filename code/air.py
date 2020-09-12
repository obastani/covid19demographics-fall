from urllib.request import urlopen, Request
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import pandas as pd

def run_air(args):
    path = "../../safegraph/air/raw/EUstations_url_historical.csv"
    links = pd.read_csv(path)
    hist_links = links["historical_url"].to_list()
    count = 0
    unable = []
    for link in hist_links:
        count += 1
        print(count)
        # Using Selenium
        # driver = webdriver.Safari()
        driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
        driver.maximize_window()
        try:
            driver.get(link)
            time.sleep(10)
            # Click button
            driver.find_element_by_xpath('//*[@id="historical-aqidata-header"]/div[3]/div[2]/div[1]/center[2]/center/div').click()
            time.sleep(12)
            # Inpt fields
            org = driver.find_element_by_xpath('//*[@id="historical-aqidata-header"]/div[3]/div[2]/div[1]/center[2]/div/center/form/div[1]/div[3]/input')
            email = driver.find_element_by_xpath('//*[@id="historical-aqidata-header"]/div[3]/div[2]/div[1]/center[2]/div/center/form/div[1]/div[2]/input')
            name = driver.find_element_by_xpath('//*[@id="historical-aqidata-header"]/div[3]/div[2]/div[1]/center[2]/div/center/form/div[1]/div[1]/input')

            org.send_keys('University of Michigan')
            time.sleep(2)
            email.send_keys('asyc@umich.edu')
            time.sleep(2)
            name.send_keys('Andrew')
            time.sleep(2)

            driver.find_element_by_xpath('//*[@id="historical-aqidata-header"]/div[3]/div[2]/div[1]/center[2]/div/center/form/div[2]/div/input').click()
            time.sleep(3)
            driver.find_element_by_xpath('//*[@id="historical-aqidata-header"]/div[3]/div[2]/div[1]/center[2]/div/center/form/div[4]').click()
            time.sleep(3)
        except:
            print("Unable to grab " + link)
            unable.append(link)
        driver.close()
    # Log of links that did not work
    with open('../../safegraph/air/data/broken_links.txt', 'w') as f:
        for item in unable:
            f.write("%s\n" % item)

if __name__ == '__main__':
    run_air({})