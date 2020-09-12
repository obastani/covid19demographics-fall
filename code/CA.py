# https://public.tableau.com/profile/melissa.taylor#!/vizhome/EpiCOVIDtest/Dashboard

import csv
from datetime import datetime
from johnutil.imgutil import getGraph, getCanvas
import os
import re, pdb
import requests
from selenium import webdriver
import sys
import numpy as np
import time
import pandas as pd


def get_digits(name, canvas, driver):
    cases = getCanvas(driver.find_element_by_xpath(canvas), driver).replace(",", "").replace(" ", "")
    reDigit = re.compile(r"(\d+)")
    match = reDigit.match(cases.strip().lower())
    if match:
        return match.group(1)
    else:
        print(f"Warning: no {name} extracted; got string", cases)
        return None

def run_new_CA():
    raw_name = '../CA/raw/'
    data_age = '../CA/data/data_age.csv'
    data_race = '../CA/data/data_race.csv'
    data_testing = '../CA/data/data_testing.csv'
    data_sex = '../CA/data/data_sex.csv'
    data_county = '../CA/data/data_county.csv'
    data_county_hosp = '../CA/data/hospital_data.csv'
    now = str(datetime.now())

    # Links
    state_age = "https://data.ca.gov/dataset/590188d5-8545-4c93-a9a0-e230f0db7290/resource/339d1c4d-77ab-44a2-9b40-745e64e335f2/download/case_demographics_age.csv"
    state_race_ethn = "https://data.ca.gov/dataset/590188d5-8545-4c93-a9a0-e230f0db7290/resource/7e477adb-d7ab-4d4b-a198-dc4c6dc634c9/download/case_demographics_ethnicity.csv"
    state_testing = "https://data.ca.gov/dataset/efd6b822-7312-477c-922b-bccb82025fbe/resource/b6648a0d-ff0a-4111-b80b-febda2ac9e09/download/statewide_testing.csv"
    state_sex = "https://data.ca.gov/dataset/590188d5-8545-4c93-a9a0-e230f0db7290/resource/ee01b266-0a04-4494-973e-93497452e85f/download/case_demographics_sex.csv"
    county_cases = "https://data.ca.gov/dataset/590188d5-8545-4c93-a9a0-e230f0db7290/resource/926fd08f-cc91-4828-af38-bd45de97f8c3/download/statewide_cases.csv"
    county_hospital = "https://data.ca.gov/dataset/529ac907-6ba1-4cb7-9aae-8966fc96aeef/resource/42d33765-20fd-44b8-a978-b083b7542225/download/hospitals_by_county.csv"

    # Out Dicts
    out_county = []
    out_county_hosp = []

    # Statewide First
    # Read to pd and collect raw
    age_df = pd.read_csv(state_age)
    race_df = pd.read_csv(state_race_ethn)
    test_df = pd.read_csv(state_testing)
    sex_df = pd.read_csv(state_sex)

    # # Save Raw
    age_df.to_csv(raw_name + now + "_age.csv")
    race_df.to_csv(raw_name + now + "_race.csv")
    test_df.to_csv(raw_name + now + "_test.csv")
    sex_df.to_csv(raw_name + now + "_sex.csv")

    # Get historical
    historical = False
    
    if historical:
        print()
        # # Age
        # age_dates = list(dict.fromkeys(age_df["date"].tolist()))
        # exp_ages = ['0-17', '18-49', '50-64', '65 and Older', 'Unknown', '65+', 'Missing']
        # for date in age_dates:
        #     csv_row = {}
        #     dt = age_df.loc[age_df['date'] == date]
        #     if len(dt.index) != 5:
        #         raise Exception("More or less age categories")
        #     for index, row in dt.iterrows():
        #         age_group = row["age_group"]
        #         if age_group == "65 and Older":
        #             age_group = "65+"
        #         elif age_group == "Missing":
        #             age_group = "Unknown"
        #         csv_row["# Cases Age [" + age_group + "]"] = row["totalpositive"]
        #         csv_row["% Cases Age [" + age_group + "]"] = row["case_percent"]
        #         csv_row["# Deaths Age [" + age_group + "]"] = row["deaths"]
        #         csv_row["% Deaths Age [" + age_group + "]"] = row["deaths_percent"]
        #     csv_row["Report Date"] = date
        #     # Export
        #     fields = sorted([x for x in csv_row])
        #     exists = os.path.exists(data_age)
        #     with open(data_age, "a") as fp:
        #         writer = csv.writer(fp)
        #         if not exists:
        #             writer.writerow(fields)
        #         writer.writerow([csv_row[x] for x in fields])

        # # Race
        # race_dates = list(dict.fromkeys(race_df["date"].tolist()))
        # races = list(dict.fromkeys(race_df["race_ethnicity"].tolist()))
        # exp_race = ['Latino', 'White', 'Asian', 'Black', 'Multiracial', 'American Indian or Alaska Native', 'Native Hawaiian or Pacific Islander', 'Other', 'Multi-Race', 'Native Hawaiian and other Pacific Islander']
        # for date in race_dates:
        #     csv_row = {}
        #     dt = race_df.loc[race_df['date'] == date]
        #     if len(dt.index) != 8:
        #         raise Exception("More or less race categories")
        #     for index, row in dt.iterrows():
        #         race_group = row["race_ethnicity"]
        #         if race_group == "Multiracial":
        #             race_group = "Multi-Race"
        #         elif race_group == "Native Hawaiian and other Pacific Islander":
        #             race_group = "Native Hawaiian or Pacific Islander"
        #         csv_row["# Cases Race/Ethnicity: " + race_group] = row["cases"]
        #         csv_row["% Cases Race/Ethnicity: " + race_group] = row["case_percentage"]
        #         csv_row["# Deaths Race/Ethnicity: " + race_group] = row["deaths"]
        #         csv_row["% Deaths Race/Ethnicity: " + race_group] = row["death_percentage"]
        #     csv_row["Report Date"] = date
        #     # Export
        #     fields = sorted([x for x in csv_row])
        #     exists = os.path.exists(data_race)
        #     with open(data_race, "a") as fp:
        #         writer = csv.writer(fp)
        #         if not exists:
        #             writer.writerow(fields)
        #         writer.writerow([csv_row[x] for x in fields])

        # # Testing
        # test_df.to_csv(data_testing)

        # # Sex
        # sex_dates = list(dict.fromkeys(sex_df["date"].tolist()))
        # sexes = list(dict.fromkeys(sex_df["sex"].tolist()))
        # exp_sexes = ['Female', 'Male', 'Unknown', 'Transgender']
        # for date in sex_dates:
        #     csv_row = {}
        #     dt = sex_df.loc[sex_df['date'] == date]
        #     dt.drop_duplicates(inplace = True)
        #     for index, row in dt.iterrows():
        #         sex_group = row["sex"]
        #         if sex_group == "Transgender":
        #             continue
        #         elif sex_group == "Unknown":
        #             csv_row["Total Cases: " + sex_group + " Sex"] = row["totalpositive2"]
        #             csv_row["% Total Cases: " + sex_group + " Sex"] = row["case_percent"]
        #             csv_row["Total Deaths: " + sex_group + " Sex"] = row["deaths"]
        #             csv_row["% Total Deaths: " + sex_group + " Sex"] = row["deaths_percent"]
        #         else:
        #             csv_row["Total Cases: " + sex_group] = row["totalpositive2"]
        #             csv_row["% Total Cases: " + sex_group] = row["case_percent"]
        #             csv_row["Total Deaths: " + sex_group] = row["deaths"]
        #             csv_row["% Total Deaths: " + sex_group] = row["deaths_percent"]
        #     csv_row["Report Date"] = date
        #     # Export
        #     fields = sorted([x for x in csv_row])
        #     exists = os.path.exists(data_sex)
        #     with open(data_sex, "a") as fp:
        #         writer = csv.writer(fp)
        #         if not exists:
        #             writer.writerow(fields)
        #         writer.writerow([csv_row[x] for x in fields])
    else:
        # Age
        path = data_age
        if not os.path.exists(data_age):
            # Getting most recent date we have
            versions = True
            count = 1
            while versions:
                if os.path.exists("../CA/data/data_age_V" + str(count) +".csv"):
                    count += 1
                else:
                    versions = False
            path = ""
            if count == 1:
                path = data_age
            else:
                path = "../CA/data/data_age_V" + str(count - 1) +".csv"
        dates = list(dict.fromkeys((pd.read_csv(path)["Report Date"]).tolist()))
        datetime_list = [datetime.strptime(x, '%Y-%m-%d') for x in dates]
        most_recent = max(dt for dt in datetime_list if dt < datetime.now())
        
        # Figuring which dates that are available to collect
        new_dates = list(dict.fromkeys((age_df["date"]).tolist()))
        raw_date_list = [datetime.strptime(x, '%Y-%m-%d') for x in new_dates]
        to_collect = [y for y in raw_date_list if y > most_recent]
        for date in to_collect:
            str_date = date.strftime('%Y-%m-%d')
            csv_row = {}
            dt = age_df.loc[age_df['date'] == str_date]
            exp_ages = ['0-17', '18-49', '50-64', '65 and Older', 'Unknown', '65+', 'Missing']
            if len(dt.index) != 5:
                raise Exception("More or less age categories")
            for index, row in dt.iterrows():
                age_group = row["age_group"]
                if age_group not in exp_ages:
                    raise Exception("Unexpected age group")
                if age_group == "65 and Older":
                    age_group = "65+"
                elif age_group == "Missing":
                    age_group = "Unknown"
                csv_row["# Cases Age [" + age_group + "]"] = row["totalpositive"]
                csv_row["% Cases Age [" + age_group + "]"] = row["case_percent"]
                csv_row["# Deaths Age [" + age_group + "]"] = row["deaths"]
                csv_row["% Deaths Age [" + age_group + "]"] = row["deaths_percent"]
            csv_row["Report Date"] = str_date
            # Export
            fields = sorted([x for x in csv_row])
            exists = os.path.exists(data_age)
            with open(data_age, "a") as fp:
                writer = csv.writer(fp)
                if not exists:
                    writer.writerow(fields)
                writer.writerow([csv_row[x] for x in fields])
        # Race
        path = data_race
        if not os.path.exists(data_race):
            # Getting most recent date we have
            versions = True
            count = 1
            while versions:
                if os.path.exists("../CA/data/data_race_V" + str(count) +".csv"):
                    count += 1
                else:
                    versions = False
            path = ""
            if count == 1:
                path = data_race
            else:
                path = "../CA/data/data_race_V" + str(count - 1) +".csv"
        dates = list(dict.fromkeys((pd.read_csv(path)["Report Date"]).tolist()))
        datetime_list = [datetime.strptime(x, '%Y-%m-%d') for x in dates]
        most_recent = max(dt for dt in datetime_list if dt < datetime.now())
        
        # Figuring which dates that are available to collect
        new_dates = list(dict.fromkeys((race_df["date"]).tolist()))
        raw_date_list = [datetime.strptime(x, '%Y-%m-%d') for x in new_dates]
        to_collect = [y for y in raw_date_list if y > most_recent]
        exp_race = ['Latino', 'White', 'Asian', 'Black', 'Multiracial', 'American Indian or Alaska Native', 'Native Hawaiian or Pacific Islander', 'Other', 'Multi-Race', 'Native Hawaiian and other Pacific Islander']
        for date in to_collect:
            csv_row = {}
            str_date = date.strftime('%Y-%m-%d')
            dt = race_df.loc[race_df['date'] == str_date]
            print(dt)
            if len(dt.index) != 8:
                raise Exception("More or less race categories")
            for index, row in dt.iterrows():
                race_group = row["race_ethnicity"]
                if race_group not in exp_race:
                    raise Exception("Unexpected Race Group")
                if race_group == "Multiracial":
                    race_group = "Multi-Race"
                elif race_group == "Native Hawaiian and other Pacific Islander":
                    race_group = "Native Hawaiian or Pacific Islander"
                csv_row["# Cases Race/Ethnicity: " + race_group] = row["cases"]
                csv_row["% Cases Race/Ethnicity: " + race_group] = row["case_percentage"]
                csv_row["# Deaths Race/Ethnicity: " + race_group] = row["deaths"]
                csv_row["% Deaths Race/Ethnicity: " + race_group] = row["death_percentage"]
            csv_row["Report Date"] = str_date
            # Export
            fields = sorted([x for x in csv_row])
            exists = os.path.exists(data_race)
            with open(data_race, "a") as fp:
                writer = csv.writer(fp)
                if not exists:
                    writer.writerow(fields)
                writer.writerow([csv_row[x] for x in fields])
        # Testing
        path = data_testing
        if not os.path.exists(data_testing):
            # Getting most recent date we have
            versions = True
            count = 1
            while versions:
                if os.path.exists("../CA/data/data_testing_V" + str(count) +".csv"):
                    count += 1
                else:
                    versions = False
            path = ""
            if count == 1:
                path = data_testing
            else:
                path = "../CA/data/data_testing_V" + str(count - 1) +".csv"
        dates = list(dict.fromkeys((pd.read_csv(path)["date"]).tolist()))
        datetime_list = [datetime.strptime(x, '%m/%d/%y') for x in dates]
        most_recent = max(dt for dt in datetime_list if dt < datetime.now())
        
        # Figuring which dates that are available to collect
        new_dates = list(dict.fromkeys((test_df["date"]).tolist()))
        raw_date_list = [datetime.strptime(x, '%Y-%m-%d') for x in new_dates]
        to_collect = [y for y in raw_date_list if y > most_recent]
        for date in to_collect:
            csv_row = {}
            str_date = date.strftime('%Y-%m-%d')
            dt = test_df.loc[test_df['date'] == str_date]
            if len(dt.index) != 1:
                raise Exception("Unexpected number of rows in testing")
            csv_row["date"] = date.strftime("%m/%d/%y")
            for index, row in dt.iterrows():
                csv_row["tested"] = row["tested"]
            fields = sorted([x for x in csv_row])
            exists = os.path.exists(data_testing)
            with open(data_testing, "a") as fp:
                writer = csv.writer(fp)
                if not exists:
                    writer.writerow(fields)
                writer.writerow([csv_row[x] for x in fields])
        # Sex
        path = data_sex
        if not os.path.exists(data_sex):
            # Getting most recent date we have
            versions = True
            count = 1
            while versions:
                if os.path.exists("../CA/data/data_sex_V" + str(count) +".csv"):
                    count += 1
                else:
                    versions = False
            path = ""
            if count == 1:
                path = data_sex
            else:
                path = "../CA/data/data_sex_V" + str(count - 1) +".csv"
        dates = list(dict.fromkeys((pd.read_csv(path)["Report Date"]).tolist()))
        datetime_list = [datetime.strptime(x, '%Y-%m-%d') for x in dates]
        most_recent = max(dt for dt in datetime_list if dt < datetime.now())
        
        # Figuring which dates that are available to collect
        new_dates = list(dict.fromkeys((test_df["date"]).tolist()))
        raw_date_list = [datetime.strptime(x, '%Y-%m-%d') for x in new_dates]
        to_collect = [y for y in raw_date_list if y > most_recent]
        exp_sexes = ['Female', 'Male', 'Unknown']
        for date in to_collect:
            csv_row = {}
            str_date = date.strftime('%Y-%m-%d')
            dt = sex_df.loc[sex_df['date'] == str_date]
            if len(dt.index) != 3:
                raise Exception("Unexpected number of Sex Groups")
            dt.drop_duplicates(inplace = True)
            for index, row in dt.iterrows():
                sex_group = row["sex"]
                if sex_group not in exp_sexes:
                    raise Exception("Unexpected sex group")
                if sex_group == "Unknown":
                    csv_row["Total Cases: " + sex_group + " Sex"] = row["totalpositive2"]
                    csv_row["% Total Cases: " + sex_group + " Sex"] = row["case_percent"]
                    csv_row["Total Deaths: " + sex_group + " Sex"] = row["deaths"]
                    csv_row["% Total Deaths: " + sex_group + " Sex"] = row["deaths_percent"]
                else:
                    csv_row["Total Cases: " + sex_group] = row["totalpositive2"]
                    csv_row["% Total Cases: " + sex_group] = row["case_percent"]
                    csv_row["Total Deaths: " + sex_group] = row["deaths"]
                    csv_row["% Total Deaths: " + sex_group] = row["deaths_percent"]
            csv_row["Report Date"] = str_date
            # Export
            fields = sorted([x for x in csv_row])
            exists = os.path.exists(data_sex)
            with open(data_sex, "a") as fp:
                writer = csv.writer(fp)
                if not exists:
                    writer.writerow(fields)
                writer.writerow([csv_row[x] for x in fields])
        
    # County level
    county_df = pd.read_csv(county_cases)
    county_hosp_df = pd.read_csv(county_hospital)
    # # Save raw
    county_df.to_csv(raw_name + now + "county_cases.csv")
    county_hosp_df.to_csv(raw_name + now + "county_hosp.csv")
    path = data_county
    if not os.path.exists(data_county):
        # Getting most recent date we have
        versions = True
        count = 1
        while versions:
            if os.path.exists("../CA/data/data_county_V" + str(count) +".csv"):
                count += 1
            else:
                versions = False
        path = ""
        if count == 1:
            path = data_county
        else:
            path = "../CA/data/data_county_V" + str(count - 1) +".csv"
    
    dates = list(dict.fromkeys((pd.read_csv(path)["date"]).tolist()))
    datetime_list = [datetime.strptime(x, '%m/%d/%y') for x in dates]
    most_recent = max(dt for dt in datetime_list if dt < datetime.now())
    
    # Figuring which dates that are available to collect
    new_dates = list(dict.fromkeys((county_df["date"]).tolist()))
    raw_date_list = [datetime.strptime(x, '%Y-%m-%d') for x in new_dates]
    to_collect = [y for y in raw_date_list if y > most_recent]
    
    exp_cols = ['county', 'totalcountconfirmed', 'totalcountdeaths', 'newcountconfirmed', 'newcountdeaths', 'date']
    for date in to_collect:
        str_date = date.strftime('%Y-%m-%d')
        dt = county_df.loc[county_df['date'] == str_date]
        rows = dt.to_dict(orient='records')
        cols = list(dt.columns)
        if len(cols) != len(exp_cols):
            raise Exception("Unexpected number of columns for county cases")
        for i in range(len(cols)):
            if cols[i] != exp_cols[i]:
                raise Exception("Unexpected order of columns for county cases")
        for row in rows:
            row['date'] = date.strftime('%m/%d/%y')
            # Export
            fields = [x for x in row]
            exists = os.path.exists(data_county)
            with open(data_county, "a") as fp:
                writer = csv.writer(fp)
                if not exists:
                    writer.writerow(fields)
                writer.writerow([row[x] for x in fields])
    
    path = data_county_hosp
    if not os.path.exists(data_county_hosp):
        # Getting most recent date we have
        versions = True
        count = 1
        while versions:
            if os.path.exists("../CA/data/hospital_data_V" + str(count) +".csv"):
                count += 1
            else:
                versions = False
        if count == 1:
            path = data_county_hosp
        else:
            path = "../CA/data/hospital_data_V" + str(count - 1) +".csv"
    dates = list(dict.fromkeys((pd.read_csv(path)["todays_date"]).tolist()))
    datetime_list = [datetime.strptime(x, '%m/%d/%y') for x in dates]
    most_recent = max(dt for dt in datetime_list if dt < datetime.now())
    
    # Figuring which dates that are available to collect
    new_dates = list(dict.fromkeys((county_hosp_df["todays_date"]).tolist()))
    raw_date_list = [datetime.strptime(x, '%Y-%m-%d') for x in new_dates]
    to_collect = [y for y in raw_date_list if y > most_recent]
    exp_cols = ["county", "todays_date", "hospitalized_covid_confirmed_patients",  "hospitalized_suspected_covid_patients",  "hospitalized_covid_patients",  "all_hospital_beds",  "icu_covid_confirmed_patients",  "icu_suspected_covid_patients",  "icu_available_beds"]
    for date in to_collect:
        str_date = date.strftime('%Y-%m-%d')
        dt = county_hosp_df.loc[county_hosp_df['todays_date'] == str_date]
        cols = list(dt.columns)
        if len(cols) != len(exp_cols):
            raise Exception("Unexpected number of columns in hospital data")
        for i in range(len(cols)):
            if cols[i] != exp_cols[i]:
                raise Exception("Unexpected order of columns in hospital data")
        rows = dt.to_dict(orient='records')
        for row in rows:
            row['todays_date'] = date.strftime('%m/%d/%y')
            # Export
            fields = [x for x in row]
            exists = os.path.exists(data_county_hosp)
            with open(data_county_hosp, "a") as fp:
                writer = csv.writer(fp)
                if not exists:
                    writer.writerow(fields)
                writer.writerow([row[x] for x in fields])


def run_CA(args):
    # Parameters
    raw_name = '../CA/raw'
    data_name = '../CA/data/data.csv'
    race_data_name = '../CA/data/race_data.csv'
    hospital_data_name = '../CA/data/hospital_data.csv'
    now = str(datetime.now())
    new = True

    if new:
        run_new_CA()
    else:
        # driver = webdriver.Safari()
        driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
        driver.maximize_window()
        driver.get("https://public.tableau.com/views/COVID-19PublicDashboard/Covid-19Public?:embed=y&:display_count=no&:showVizHome=no")
        time.sleep(10)  # More robust to wait for elements to appear...
        #driver.switch_to.frame("viz_embedded_frame")


        out = {}
        
        out["TotalCases"] = get_digits("TotalCases", 
                '//*[@id="view8860806102834544352_2954032034214900649"]/div[1]/div[2]/canvas[1]', driver)
        out["TotalFatalities"] = get_digits("TotalFatalities", 
                '//*[@id="view8860806102834544352_10936283936734129650"]/div[1]/div[2]/canvas[1]', driver)
        out["TotalTested"] = get_digits("TotalTested", 
                '//*[@id="view8860806102834544352_12188172174700680575"]/div[1]/div[2]/canvas[1]', driver)

        age_groups = getCanvas(driver.find_element_by_xpath(
            '//*[@id="tabZoneId257"]/div/div/div/div/div[5]/div[1]/canvas'), driver).replace("\n", " ")
        age_text = age_groups.replace(".", "-")
        try: 
            age_perc = getCanvas(driver.find_element_by_xpath('//*[@id="view8860806102834544352_11651535759491462876"]/div[1]/div[2]/canvas[1]'), driver).replace("\n", " ")
            age_text = f"{age_text} {age_perc}"
        except:
            pass 
        age_cats_together = True
        five_cats = False
        #match = re.search(
        #        "([\d,-]+)[ ]+([\d,-]+)[ ]+([\d,-]+)[ ]+([A-Z][a-z]+)[ ]+([\d]+)%[ ]+([\d]+)%[ ]+([\d]+)%[ ]+([\d]+)%", age_text)
        match = re.search(
                "([\d,-]+)[ ]+([\d,-]+)[ ]+([\d,-]+)[ ]+([\d,+]+)[ ]+[‘]*([A-Z][a-z]+)[ ]+([\d]+)%[ ]+([\d]+)%[ ]+([\d]+)%[ ]+([\d]+)%[ ]+([\d]+)%", age_text)
        if match is None:
            match = re.search("([\d,-]+)[ ]+([\d,-]+)[ ]+([\d,-]+)[ ]+([\d,-]+)[ ]+([A-Z][a-z]+)[ ]+([\d]+%[ ]*)+", age_text)
            five_cats = match is not None
        #if match is None:
        #    match = re.search(
        #        "([\d]+)[ ]+([\d]+)%[ ]+([\d,-]+)[ ]+([\d]+)%[ ]+([\d,-]+)[ ]+([\d]+)%[ ]+([\d,+]+)[ ]+([\d]+)%", age_text)
        #    age_cats_together = False
        if match is None:
            raise KeyError ("Failed at finding age groups")
        else: 
            #age_groups = [f"Age_{i}" for i in match.groups()[::2]]
            #age_percentages =  [int(i) for i in match.groups()[1::2]]
            if age_cats_together:
                if not five_cats:
                    age_groups = [f"Age_{i}" for i in match.groups()[:len(match.groups())//2]]
                    age_percentages =  [int(i) for i in match.groups()[len(match.groups())//2:]]
                else: 
                    age_groups = [f"Age_{i}" for i in match.groups()[:5]]
                    age_percentages =  [int(i.replace("%", "")) for i in re.findall("[\d]+%", age_text)]
                    if len(age_percentages)==3:
                        age_percentages = [np.nan] + age_percentages + [np.nan]
            else:
                raise Exception("Not implemented")
        #unknown_age = getCanvas(driver.find_element_by_xpath('//*[@id="view8860806102834544352_17557392999253321305"]/div[1]/div[2]/canvas[2]'), driver)
        #match = re.search("([\d]+)%", unknown_age)
        #if match is None:
        #    u_age = np.nan
        #    raise Exception("Failed at collecting unkown age")
        #else:
        #     u_age = int(match.groups()[0])
        #age_groups.append("Age_Unknown")
        #age_percentages.append(u_age)
        for title, cnt in zip(age_groups, age_percentages):
            out[title] = cnt

        # Figure out how to do this...
        #ages = getGraph(driver.find_element_by_xpath('//*[@id="view8860806102834544352_11651535759491462876"]/div[1]/div[2]/canvas[1]'), driver)
        #ages = getCanvas(driver.find_element_by_xpath('//*[@id="view8860806102834544352_11651535759491462876"]/div[1]/div[2]/canvas[1]'), driver)
        #match = re.search("([\d]+)[ ]+[\d,-]+%[ ]+([\d,-]+)[ ]+[\d]+%[ ]+([\d,-]+)[ ]+[\d]+%[ ]+([\d,-]+)[ ]+[\d]+%", age_groups)

        # Sex
        #male = getCanvas(driver.find_element_by_xpath('//*[@id="view8860806102834544352_4610613615443112592"]/div[1]/div[2]/canvas[2]'), driver)
        #//*[@id="view8860806102834544352_4610613615443112592"]/div[1]/div[2]/canvas[1]
        #//*[@id="view8860806102834544352_4610613615443112592"]/div[1]/div[2]/canvas[2]
        #/html/body/div[2]/div[2]/div[1]/div[1]/div/div[2]/div[43]/div/div/div/div/div[11]/div[1]/div[2]/canvas[2]
        #male_match = re.search("([\d]+)%", male)
        #female = getCanvas(driver.find_element_by_xpath('//*[@id="view8860806102834544352_15384157321978781716"]/div[1]/div[2]/canvas[1]'), driver)
        #female_match = re.search("([\d]+)%", female)
        #unknown = getCanvas(driver.find_element_by_xpath('//*[@id="view8860806102834544352_6009561529893989681"]/div[1]/div[2]/canvas[2]'), driver)
        #//*[@id="view8860806102834544352_6009561529893989681"]/div[1]/div[2]/canvas[2]
        #//*[@id="view8860806102834544352_6009561529893989681"]/div[1]/div[2]/canvas[1]
            #'//*[@id="view8860806102834544352_6009561529893989681"]/div[2]/div[2]/canvas[1]'), driver)
        #unknown_match = re.search("([\d]+)%", unknown)
        #if (unknown_match is None) + (female_match is None) + (male_match is None)>1:
        #    raise Exception("Cound not collect gender information")
        #else: 
        sex = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId247"]/div/div/div/div/div[5]/div[1]/canvas'), driver)
        sex = sex.replace("‘", "").replace("\n\n", " ")
        sex_perc = getCanvas(driver.find_element_by_xpath('//*[@id="view8860806102834544352_15384157321978781716"]/div[1]/div[2]/canvas[1]'), driver).replace("\n\n", " ")
        sex = f"{sex}\n\n{sex_perc}"
        match = re.search("Female\nMale Unknown\n\n([\d]+)% ([\d]+)% ([\d]+)%", sex)
        out["male_pos"] = int(match.groups()[1]) if match is not None else np.nan
        out["female_pos"] = int(match.groups()[0]) if match is not None else np.nan
        out["sex_unknown_pos"] = int(match.groups()[2]) if match is not None else np.nan
        #Race/ethnicity
        race = getCanvas(driver.find_element_by_xpath('//*[@id="tabZoneId246"]/div/div/div/div[1]/div[5]/div[1]/canvas'), driver)
        race_perc = getCanvas(driver.find_element_by_xpath('//*[@id="view8860806102834544352_2377024103324179123"]/div[1]/div[2]/canvas[1]'), driver)
        race = race.split("\n") + race_perc.split("\n")
        race = list(filter(len, race))
        
        if len(race)!=16: 
            raise ValueError("incorrect number of races")
        def fk_every_dk(x):
            try:
                value = int(x.replace("%", ""))
            except ValueError:
                value = np.nan
            return value

        race_cats = map(lambda x: x.replace('‘', "").replace(".", ""), race[:8])
        race_perc = map(fk_every_dk , race[8:])
        out_race = {x:y for x,y in zip(race_cats, race_perc)}

        driver.close()
            
        out["Scrape_Time"] = now
        fields = sorted([x for x in out])
        exists = os.path.exists(data_name)
        with open(data_name, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([out[x] for x in fields])

        # Let's make a best effort to get the raw data...
        img = requests.get("https://public.tableau.com/static/images/CO/COVID-19PublicDashboard/Covid-19Public/1_rss.png")

        out_race["Scrape_Time"] = now
        fields = sorted([x for x in out_race])
        exists = os.path.exists(race_data_name)
        with open(race_data_name, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([out_race[x] for x in fields])

        with open("%s/%s.png" % (raw_name, now), "wb") as fp:
            fp.write(img.content)

        # California hospital situation 
        # driver = webdriver.Safari()
        driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
        driver.get("https://public.tableau.com/views/COVID-19PublicDashboard/Covid-19Hospitals?%3Aembed=y&%3Adisplay_count=no&%3AshowVizHome=no")
        time.sleep(10)  # More robust to wait for elements to appear...
        driver.implicitly_wait(5) 
        stoi = lambda x: int(x.replace(",", ""))
        out = {}
        out["posPatients"] = get_digits("PosPatients", 
                '//*[@id="view11327846829742299964_9307352602670595869"]/div[1]/div[2]/canvas[1]', driver)
        out["posICU"] = get_digits("PosICU", 
                '//*[@id="view11327846829742299964_7957542083138737667"]/div[1]/div[2]/canvas[1]', driver)
        out["suspectedICU"] = get_digits("suspectedICU", 
                '//*[@id="view11327846829742299964_12557426117314542746"]/div[1]/div[2]/canvas[1]', driver)
        out["suspectedPatients"] = get_digits("suspectedPatients", 
                '//*[@id="view11327846829742299964_7498269305876793953"]/div[1]/div[2]/canvas[1]', driver)
        responding_fasilities = getCanvas(driver.find_element_by_xpath(
            '//*[@id="view11327846829742299964_17652355579425549403"]/div[1]/div[2]/canvas[1]'), driver)
        responding_beds = getCanvas(driver.find_element_by_xpath(
            '//*[@id="view11327846829742299964_12615353459920747640"]/div[1]/div[2]/canvas[1]'), driver)
        #match = re.search("[No]*\n\n([0-9]+)%\n\n[Yes\n]*([\d]+)", responding_fasilities)
        match = re.search("([\d,,]+) of ([\d,,]+)", responding_fasilities)
        #out["responding_facilities_yes_percent"] = int(match.groups()[0]) if match is not None else np.nan
        out["responding_facilities_yes_percent"] = stoi(match.groups()[0])/stoi(match.groups()[1])
        #out["responding_fasilities_yes_num"] = int(match.groups()[1].replace(",", "")) if match is not None else np.nan
        out["responding_fasilities_yes_num"] = stoi(match.groups()[1])

        #match = re.search("([\d,,]+)\n[\d\d%\n]*Yes[:]*\n([\d,,]+)", responding_beds)
        match = re.search("([\d,,]+) of ([\d,,]+)", responding_beds)
        #out["responding_beds_no_num"] = int(match.groups()[0].replace(",", "")) if match is not None else np.nan
        #out["responding_beds_yes_num"] = int(match.groups()[1].replace(",", "")) if match is not None else np.nan
        out["responding_beds_no_num"] = stoi(match.groups()[1]) - stoi(match.groups()[0])
        out["responding_beds_yes_num"] = stoi(match.groups()[1])
        driver.close()
            
        out["Scrape_Time"] = now
        fields = sorted([x for x in out])
        exists = os.path.exists(hospital_data_name)
        with open(hospital_data_name, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([out[x] for x in fields])  
        img = requests.get("https://public.tableau.com/static/images/CO/COVID-19PublicDashboard/Covid-19Hospitals/1_rss.png")
        with open("%s/%s_hospital.png" % (raw_name, now), "wb") as fp:
            fp.write(img.content)




if __name__ == '__main__':
    run_CA({})
