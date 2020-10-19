# There is only data available for one day.
import camelot
import ghostscript
import requests
import sys
import os
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from urllib.request import urlopen
from zipfile import ZipFile
import pandas as pd
import numpy as np
import csv

def get_historical():
    raw_name = '../MS/raw'
    # Count is the code in the URL for the first available file
    count = 8697
    month = 6
    day = 21
    base_url = "https://msdh.ms.gov/msdhsite/_static/resources/"
    # Loop until last file available with code 8710
    while count != 8711:
        # Write pdf to raw
        url = base_url + str(count) + ".pdf"
        r = requests.get(url, allow_redirects=True)
        with open(raw_name + "/" + "0" + str(month) + "_" + str(day) + "_summary.pdf", "wb") as f:
            f.write(r.content)
        count += 1
        if day == 30:
            day = 1
            month = 7
        else:
            day += 1

def format_df(raw_name, file, out_cases, out_deaths):
    # Getting dates
    name_list = file.split("_")
    month = name_list[0]
    day = name_list[1]
    cat = name_list[3].replace(".zip", "")
    full_date = month + "/" + day + "/2020"

    # Expected headers
    expected_headers_0 = [np.nan, np.nan, 'Not Hispanic', np.nan, np.nan, np.nan, np.nan, np.nan, 'Hispanic', np.nan, np.nan, np.nan, np.nan, np.nan, 'Unknown Ethnicity', np.nan, np.nan, np.nan, np.nan, np.nan]
    expected_headers_1 = ['County', 'Total Cases', 'Black or African \nAmerican', 'White', 'American \nIndian or Alaska \nNative', 'Asian', 'Other', 'Unknown', 'Black or African \nAmerican', 'White', 'American \nIndian or Alaska \nNative', 'Asian', 'Other', 'Unknown', 'Black or African \nAmerican', 'White', 'American \nIndian or Alaska \nNative', 'Asian', 'Other', 'Unknown']
    expected_headers_1_deaths = ['County', 'Total Deaths', 'Black or African \nAmerican', 'White', 'American \nIndian or Alaska \nNative', 'Asian', 'Other', 'Unknown', 'Black or African \nAmerican', 'White', 'American \nIndian or Alaska \nNative', 'Asian', 'Other', 'Unknown', 'Black or African \nAmerican', 'White', 'American \nIndian or Alaska \nNative', 'Asian', 'Other', 'Unknown']
    # Read csvs to pandas
    zip_file = ZipFile(raw_name + "/" + file)
    for csv_file in zip_file.infolist():
        if ".csv" in csv_file.filename:
            df = pd.read_csv(zip_file.open(csv_file.filename))
            # Renaming column so it can be indexed
            df.rename(columns = {'Cases by Race and Ethnicity': "Unnamed: 2"}, inplace = True)
            # Looping through each row
            for index, row in df.iterrows():
                # Checking the columns match to expected
                if index == 0:
                    this = [x for x in row]
                    if len(this) != len(expected_headers_0):
                        raise Exception("Unequal number of headers in " + cat + " for " + full_date)
                    else:
                        if expected_headers_0[2] != "Not Hispanic":
                            raise Exception("Unexpected order of headers in " + cat + " for " + full_date)
                        elif expected_headers_0[8] != "Hispanic":
                            raise Exception("Unexpected order of headers in " + cat + " for " + full_date)
                        elif expected_headers_0[14] != "Unknown Ethnicity":
                            raise Exception("Unexpected order of headers in " + cat + " for " + full_date)
                elif index == 1:
                    this = [x for x in row]
                    if len(this) != len(expected_headers_1):
                        raise Exception("Unequal number of headers in " + cat + " for " + full_date)
                    else:
                        if cat == "cases":
                            for i in range(len(this)):
                                if this[i] != expected_headers_1[i]:
                                    print([x for x in this])
                                    raise Exception("Unexpected order of headers in " + cat + " for " + full_date)
                        elif cat == "deaths":
                            for i in range(len(this)):
                                if this[i] != expected_headers_1_deaths[i]:
                                    print([x for x in this])
                                    raise Exception("Unexpected order of headers in " + cat + " for " + full_date)
                else:
                    # Appending to respective list
                    if cat == "cases":
                        if len(row) != 20:
                            raise Exception("Unexpected number of columns")
                        county = {
                                    "Report Date": full_date,
                                    "County Name": row[0], 
                                    "Total Cases": row[1],
                                    "# Cases Race/Ethnicity: Black or African American (Not Hispanic)": row[2],
                                    "# Cases Race/Ethnicity: White (Not Hispanic)": row[3],
                                    "# Cases Race/Ethnicity: American Indian or Alaska Native (Not Hispanic)": row[4],
                                    "# Cases Race/Ethnicity: Asian (Not Hispanic)": row[5],
                                    "# Cases Race/Ethnicity: Other Race (Not Hispanic)": row[6],
                                    "# Cases Race/Ethnicity: Unknown Race (Not Hispanic)": row[7],
                                    "# Cases Race/Ethnicity: Black or African American (Hispanic)": row[8],
                                    "# Cases Race/Ethnicity: White (Hispanic)": row[9],
                                    "# Cases Race/Ethnicity: American Indian or Alaska Native (Hispanic)": row[10],
                                    "# Cases Race/Ethnicity: Asian (Hispanic)": row[11],
                                    "# Cases Race/Ethnicity: Other Race (Hispanic)": row[12],
                                    "# Cases Race/Ethnicity: Unknown Race (Hispanic)": row[13],
                                    "# Cases Race/Ethnicity: Black or African American (Unknown Ethnicity)": row[14],
                                    "# Cases Race/Ethnicity: White (Unknown Ethnicity)": row[15],
                                    "# Cases Race/Ethnicity: American Indian or Alaska Native (Unknown Ethnicity)": row[16],
                                    "# Cases Race/Ethnicity: Asian (Unknown Ethnicity)": row[17],
                                    "# Cases Race/Ethnicity: Other Race (Unknown Ethnicity)": row[18],
                                    "# Cases Race/Ethnicity: Unknown Race (Unknown Ethnicity)": row[19],
                        }
                        out_cases.append(county)
                    elif cat == "deaths":
                        if len(row) != 20:
                            raise Exception("Unexpected number of columns")
                        county = {
                                    "Report Date": full_date,
                                    "County Name": row[0], 
                                    "Total Deaths": row[1],
                                    "# Deaths Race/Ethnicity: Black or African American (Not Hispanic)": row[2],
                                    "# Deaths Race/Ethnicity: White (Not Hispanic)": row[3],
                                    "# Deaths Race/Ethnicity: American Indian or Alaska Native (Not Hispanic)": row[4],
                                    "# Deaths Race/Ethnicity: Asian (Not Hispanic)": row[5],
                                    "# Deaths Race/Ethnicity: Other Race (Not Hispanic)": row[6],
                                    "# Deaths Race/Ethnicity: Unknown Race (Not Hispanic)": row[7],
                                    "# Deaths Race/Ethnicity: Black or African American (Hispanic)": row[8],
                                    "# Deaths Race/Ethnicity: White (Hispanic)": row[9],
                                    "# Deaths Race/Ethnicity: American Indian or Alaska Native (Hispanic)": row[10],
                                    "# Deaths Race/Ethnicity: Asian (Hispanic)": row[11],
                                    "# Deaths Race/Ethnicity: Other Race (Hispanic)": row[12],
                                    "# Deaths Race/Ethnicity: Unknown Race (Hispanic)": row[13],
                                    "# Deaths Race/Ethnicity: Black or African American (Unknown Ethnicity)": row[14],
                                    "# Deaths Race/Ethnicity: White (Unknown Ethnicity)": row[15],
                                    "# Deaths Race/Ethnicity: American Indian or Alaska Native (Unknown Ethnicity)": row[16],
                                    "# Deaths Race/Ethnicity: Asian (Unknown Ethnicity)": row[17],
                                    "# Deaths Race/Ethnicity: Other Race (Unknown Ethnicity)": row[18],
                                    "# Deaths Race/Ethnicity: Unknown Race (Unknown Ethnicity)": row[19],
                        }
                        out_deaths.append(county)
    return out_cases, out_deaths


def process():
    raw_name = '../MS/raw'
    out_county = []
    # Loop through each pdf and convert to csv and format
    for file in os.listdir(raw_name):
        if ".pdf" in file:
            date = (file.replace(raw_name + "/", "")).replace("_summary.pdf", "").split("_") 
            month = date[0]
            day = date[1]
            full_date = month + "/" + day + "/2020"
            path = raw_name + "/" + file
            county_tables = camelot.read_pdf(path, pages="1,2")
            deaths_tables = camelot.read_pdf(path, pages="3,4")
            # Function to export to data.csv
            county_tables.export(path.replace(".pdf", "_cases.csv"), compress=True)
            deaths_tables.export(path.replace(".pdf", "_deaths.csv"), compress=True)
    print(out_county)

def export(out_cases, out_deaths):
    # Dir
    data_name_cases = '../MS/data/data_cases.csv'
    data_name_deaths = '../MS/data/data_deaths.csv'
    # Output - cases
    for county in out_cases:
        fields = sorted([x for x in county])
        exists = os.path.exists(data_name_cases)
        with open(data_name_cases, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([county[x] for x in fields])

    # Output - cases
    for county in out_deaths:
        fields = sorted([x for x in county])
        exists = os.path.exists(data_name_deaths)
        with open(data_name_deaths, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([county[x] for x in fields])
    
def concat():
    raw_name = '../MS/raw'
    out_cases = []
    out_deaths = []
    for file in os.listdir(raw_name):
        if ".zip" in file:
            out_cases, out_deaths = format_df(raw_name, file, out_cases, out_deaths)
    export(out_cases, out_deaths)
    

def run_MS(args):
    raw_name = '../MS/raw'
    # Get historical
    hist = False
    if hist:
        get_historical()
    else:
        process_hist = False
        if process_hist:
            # process()
            concat()
        else:
            today = date.today()
            # Get raw pdf
            base_url = "https://msdh.ms.gov/msdhsite/_static/"
            html = urlopen("https://msdh.ms.gov/msdhsite/_static/14,0,420,884.html").read()
            soup = BeautifulSoup(html, "html.parser")
            today_str = today.strftime("%m/%d/%Y")
            # today_str = "09/15/2020"
            try:
                uploaded = soup.find("li", {"data-dateapproved": today_str})
                children = uploaded.findChildren("a", recursive=False)
            except:
                print("No data file available for today")
                raise
            href = ""
            for child in children:
                href = child['href']
            url = base_url + href
            r = requests.get(url, allow_redirects=True)
            new_path = raw_name + "/" + "0" + str(today.month) + "_" + str(today.day) + "_summary.pdf"
            with open(new_path, "wb") as f:
                f.write(r.content)
            try:
                county_tables = camelot.read_pdf(new_path, pages="1,2")
                deaths_tables = camelot.read_pdf(new_path, pages="3,4")
            except:
                print("Unable to collect " + str(today) + " pdf")
            
            # Getting pre-processed raw
            county_tables.export(new_path.replace(".pdf", "_cases.csv"), compress=True)
            deaths_tables.export(new_path.replace(".pdf", "_deaths.csv"), compress=True)

            print("Collected raw for MS")

            # # Adding to data file
            # out_cases = []
            # out_deaths = []
            # file_cases = "0" + str(today.month) + "_" + str(today.day) + "_summary_cases.zip"
            # file_deaths = "0" + str(today.month) + "_" + str(today.day) + "_summary_deaths.zip"
            # out_cases, out_deaths = format_df(raw_name, file_cases, out_cases, out_deaths)
            # out_cases, out_deaths = format_df(raw_name, file_deaths, out_cases, out_deaths)
            # export(out_cases, out_deaths)

if __name__ == '__main__':
    run_MS({})
