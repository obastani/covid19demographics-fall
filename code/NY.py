# https://github.com/nychealth/coronavirus-data
import io
import requests
import pandas as pd
from datetime import datetime
from datetime import date
import os
import csv

def grabData(url, fname):
    # Read CSV url
    try: 
        df = pd.read_csv(url, error_bad_lines=False)
    except:
        print("Error reading CSV file from URL")
        raise
    # Writing to raw folder
    try: 
        df.to_csv(fname)   
    except:
        print("Unable to save raw data to path")
        raise
    return df

def processData(list_df, fields):
    values = []
    # Iterate through all the different dataframes that contain the data
    for df in list_df:
        data = df["data"]
        if df["name"] == "by-age.csv":
            try:
                ages = data["AGE_GROUP"].tolist()
                cases = data["CASE_RATE"].tolist()
                hospitalized = data["HOSPITALIZED_RATE"].tolist()
                death = data["DEATH_RATE"].tolist()
                case_count = data["CASE_COUNT"].tolist()
                hosp_count = data["HOSPITALIZED_COUNT"].tolist()
                death_count = data["DEATH_COUNT"].tolist()
            except:
                print("Change in field name in by-age.csv")
                raise
            expected_ages = ["0-17", "18-44", "45-64", "65-74", "75+", "Citywide"]
            for cur, exp in zip(ages, expected_ages):
                if cur != exp:
                    raise Exception("Unexpected Age group or order")
            # Adding to list of values in the same order as the fields list
            values.extend(cases)
            values.extend(hospitalized)
            values.extend(death)
            values.extend(case_count)
            values.extend(hosp_count)
            values.extend(death_count)
        elif df["name"] == "by-sex.csv":
            try:
                # Remove citywide rates to avoid redundancy

                data = data[~data.SEX_GROUP.str.contains("Citywide")]
                sex = data["SEX_GROUP"].tolist()
                cases = data["CASE_RATE"].tolist()
                hospitalized = data["HOSPITALIZED_RATE"].tolist()
                death = data["DEATH_RATE"].tolist()
                case_count = data["CASE_COUNT"].tolist()
                hosp_count = data["HOSPITALIZED_COUNT"].tolist()
                death_count = data["DEATH_COUNT"].tolist()
            except:
                print("Change in field name in by-sex.csv")
                raise
            # Check order and vals
            expected_sex = ["Female", "Male"]
            for cur, exp in zip(sex, expected_sex):
                if cur != exp:
                    raise Exception("Unexpected Sex group or order")
            
            # Adding to list of values in the same order as the fields list
            values.extend(cases)
            values.extend(hospitalized)
            values.extend(death)
            values.extend(case_count)
            values.extend(hosp_count)
            values.extend(death_count)
        elif df["name"] == "case-hosp-death.csv":
            # Get only last day data
            data = data.iloc[-1]
            try:
                # Adding to list of values in the same order as the fields list
                values.append(data["CASE_COUNT"])
                values.append(data["HOSPITALIZED_COUNT"])
                values.append(data["DEATH_COUNT"])
            except:
                print("Change in field name in case-hosp-death.csv")
                raise
        elif df["name"] == "by-race.csv":
            try:
                races = data["RACE_GROUP"].tolist()
                cases = data["CASE_RATE_ADJ"].tolist()
                hospitalized = data["HOSPITALIZED_RATE_ADJ"].tolist()
                death = data["DEATH_RATE_ADJ"].tolist()
                case_count = data["CASE_COUNT"].tolist()
                hosp_count = data["HOSPITALIZED_COUNT"].tolist()
                death_count = data["DEATH_COUNT"].tolist()
            except:
                print("Change in field name in by-race.csv")
                raise

            # Check order and vals
            expected_races = ["Asian/Pacific-Islander", "Black/African-American", "Hispanic/Latino", "White"]
            for cur, exp in zip(races, expected_races):
                if cur != exp:
                    raise Exception("Unexpected Race group or order")
            
            # Adding to list of values in the same order as the fields list
            values.extend(cases)
            values.extend(hospitalized)
            values.extend(death)
            values.extend(case_count)
            values.extend(hosp_count)
            values.extend(death_count)
        else:
            raise Exception("Unexpected CSV file")

    # Create resulting dictionary of values
    result_dict = {}
    # Creates the key, value pairs using fields and values list
    # Assumes both lists are in the same order
    for i in range(len(fields)):
        result_dict[fields[i]] = values[i]

    return result_dict

def grabHistorical(csv_files, raw_name):
    # Base URL for the different commits
    base = "https://raw.githubusercontent.com/nychealth/coronavirus-data/"
    commits = [
                {"commit": "81fcf12be08aadd730d1d39c153e3fd9ab371e77", "date": date(2020, 4, 28)},
                {"commit": "c68db06972c3100297a615ba397245eff8b3ee9f", "date": date(2020, 4, 29)}
              ]
    return_df = []
    # Grabbing raw data and returning data to main
    for commit in commits:
        commit_csv_list = []
        for file in csv_files:
            df = grabData(base + commit["commit"] + "/" + file, "%s/%s_"  % (raw_name, commit["date"]) + file)
            commit_csv_list.append({"name": file , "data": df, "date": commit["date"]})
        return_df.append(commit_csv_list)
    return return_df

def run_NY(args):
    # Parameters
    fetch_historical = False # Change this to fetch historical data from before we set scrape
    raw_name = '../NY/raw'
    data_name = '../NY/data/data.csv'
    now = str(datetime.now())
    baseurl = "https://raw.githubusercontent.com/nychealth/coronavirus-data/master/"
    csv_files = ["by-age.csv",
                 "by-sex.csv",
                 "case-hosp-death.csv",
                 "by-race.csv"
                ]

    # Grab data
    list_df = []
    if not fetch_historical:
        # Use of buffer list to create a list of lists of dictionaries to fit format in case we want to get historical data
        buffer_list = []
        for file in csv_files:
            df = grabData(baseurl + file, "%s/%s_"  % (raw_name, now) + file)
            buffer_list.append({"name": file, "data": df, "date": now})
        list_df.append(buffer_list)
    else:
        list_df = grabHistorical(csv_files, raw_name)
    # Output   
    # Expected fields from the data
    fields = [
              "0_17_COVID_CASE_RATE",
              "18_44_COVID_CASE_RATE",
              "45_64_COVID_CASE_RATE",
              "65_74_COVID_CASE_RATE",
              "75+_COVID_CASE_RATE",
              "City_Total_COVID_CASE_RATE",
              "0_17_HOSPITALIZED_CASE_RATE",
              "18_44_HOSPITALIZED_CASE_RATE",
              "45_64_HOSPITALIZED_CASE_RATE",
              "65_74_HOSPITALIZED_CASE_RATE",
              "75+_HOSPITALIZED_CASE_RATE",
              "City_Total_HOSPITALIZED_CASE_RATE",
              "0_17_DEATH_RATE",
              "18_44_DEATH_RATE",
              "45_64_DEATH_RATE",
              "65_74_DEATH_RATE",
              "75+_DEATH_RATE",              
              "City_Total_DEATH_RATE",
              "0_17_CASE_COUNT",
              "18_44_CASE_COUNT",
              "45_64_CASE_COUNT",
              "65_74_CASE_COUNT",
              "75+_CASE_COUNT",             
              "City_Total_CASE_COUNT",
              "0_17_HOSP_COUNT",
              "18_44_HOSP_COUNT",
              "45_64_HOSP_COUNT",
              "65_74_HOSP_COUNT",
              "75+_HOSP_COUNT",             
              "City_Total_HOSP_COUNT",
              "0_17_DEATH_COUNT",
              "18_44_DEATH_COUNT",
              "45_64_DEATH_COUNT",
              "65_74_DEATH_COUNT",
              "75+_DEATH_COUNT",             
              "City_Total_DEATH_COUNT",
              "Female_COVID_CASE_RATE",
              "Male_COVID_CASE_RATE",
              "Female_HOSPITALIZED_CASE_RATE",
              "Male_HOSPITALIZED_CASE_RATE",
              "Female_DEATH_RATE",
              "Male_DEATH_RATE",
              "Female_CASE_COUNT",
              "Male_CASE_COUNT",
              "Female_HOSP_COUNT",
              "Male_HOSP_COUNT",
              "Female_DEATH_COUNT",
              "Male_DEATH_COUNT",
              "CASE_COUNT",
              "HOSPITALIZED_COUNT",
              "DEATH_COUNT",
              "Race_Asian/Pacific-Islander_COVID_CASE_RATE",
              "Race_Black/African-American_COVID_CASE_RATE",
              "Race_Hispanic/Latino_COVID_CASE_RATE",
              "Race_White_COVID_CASE_RATE",
              "Race_Asian/Pacific-Islander_HOSPITALIZED_RATE",
              "Race_Black/African-American_HOSPITALIZED_RATE",
              "Race_Hispanic/Latino_HOSPITALIZED_RATE",
              "Race_White_HOSPITALIZED_RATE",
              "Race_Asian/Pacific-Islander_DEATH_RATE",
              "Race_Black/African-American_DEATH_RATE",
              "Race_Hispanic/Latino_DEATH_RATE",
              "Race_White_DEATH_RATE",
              "Race_Asian/Pacific-Islander_CASE_COUNT",
              "Race_Black/African-American_CASE_COUNT",
              "Race_Hispanic/Latino_CASE_COUNT",
              "Race_White_CASE_COUNT",
              "Race_Asian/Pacific-Islander_HOSPITALIZED_COUNT",
              "Race_Black/African-American_HOSPITALIZED_COUNT",
              "Race_Hispanic/Latino_HOSPITALIZED_COUNT",
              "Race_White_HOSPITALIZED_COUNT",
              "Race_Asian/Pacific-Islander_DEATH_COUNT",
              "Race_Black/African-American_DEATH_COUNT",
              "Race_Hispanic/Latino_DEATH_COUNT",
              "Race_White_DEATH_COUNT",
             ]

    # Output dictionary is created to be able to write to file - iterates through all the different dates in the list_df
    for date_file in list_df:
        exists = os.path.exists(data_name)    
        out = processData(date_file, fields)
        # Set scrape time to date of commit or now if current 
        if not fetch_historical:
            out["Scrape_Time"] = now
        else: 
            out["Scrape_Time"] = date_file[0]["date"]
        out_fields = [x for x in out]
        with open(data_name, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(out_fields)
            writer.writerow([out[x] for x in out_fields])

if __name__ == '__main__':
    run_NY({})