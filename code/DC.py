from datetime import datetime
import requests
from openpyxl import load_workbook
import pandas as pd
import os
import csv

def run_DC(args):
    # Parameters
    raw_name = '../DC/raw'
    data_name = '../DC/data/data.csv'
    now = str(datetime.now())

    r = requests.get("https://dcgov.app.box.com/index.php?rm=box_download_shared_file&vanity_name=DCHealthStatisticsData&file_id=f_645422184765")
    filename = ""
    if not r.ok:
        raise Exception("DC data download failed")
    with open("%s/%s.xlsx" % (raw_name, now), "wb") as fp:
        fp.write(r.content)
        filename = fp.name

    # filename = raw_name + "/2020-09-29.xlsx"
    
    age_gender_df = pd.read_excel(filename, sheet_name="Total Cases by Age and Gender")
    race_case_df = pd.read_excel(filename, sheet_name="Total Cases by Race")
    race_death_df = pd.read_excel(filename, sheet_name="Lives Lost by Race")
    test_hosp_df = pd.read_excel(filename, sheet_name="Overall Stats")

    new_race_case_df = race_case_df.iloc[:,[0,1,-1]].dropna()
    new_race_death_df = race_death_df.iloc[:,[0,-1]].dropna()
    new_test_hosp_df = test_hosp_df.iloc[:,[1,-1]].dropna()

    #Age
    out = {}
    out_columns = [
                    "Age [0-4]: Female Cases",
                    "Age [5-14]: Female Cases",
                    "Age [15-19]: Female Cases",
                    "Age [20-24]: Female Cases",
                    "Age [25-34]: Female Cases",
                    "Age [35-44]: Female Cases",
                    "Age [45-54]: Female Cases",
                    "Age [55-64]: Female Cases",
                    "Age [65-74]: Female Cases",
                    "Age [75+]: Female Cases",
                    "Age [0-4]: Male Cases",
                    "Age [5-14]: Male Cases",
                    "Age [15-19]: Male Cases",
                    "Age [20-24]: Male Cases",
                    "Age [25-34]: Male Cases",
                    "Age [35-44]: Male Cases",
                    "Age [45-54]: Male Cases",
                    "Age [55-64]: Male Cases",
                    "Age [65-74]: Male Cases",
                    "Age [75+]: Male Cases"
                  ]
    try:
        age_gender_df.rename(columns = {"Patient Age (Yrs)": "Age",
                                        "Female":"Female Cases",
                                        "Male":"Male Cases"}, 
                            inplace=True)
    except:
        print("Unexpected column name in raw file")
        raise

    # Drop All ages row
    if str(age_gender_df.tail(1)['Age'].values[0]) == 'nan':
        # Drop last row
        age_gender_df = age_gender_df.drop(age_gender_df.tail(1).index)
    age_gender_df = age_gender_df[~age_gender_df.Age.str.contains("All")]
    age_gender_df = age_gender_df[~age_gender_df.Age.str.contains("Unknown")]
    
    for index, row in age_gender_df.iterrows():
        age = row['Age'].strip()
        if ("Age [" + age + "]: Female Cases") not in out_columns or\
            ("Age [" + age + "]: Male Cases") not in out_columns:
            raise Exception("Unexpected age label " + age)
        
        # Add cases per age and gender to out dict
        out["Age [" + age + "]: Female Cases"] = row["Female Cases"]
        out["Age [" + age + "]: Male Cases"] = row["Male Cases"]
    
    # Add Race data - Case
    exp_races = ['Unknown', 'White', 'Black', 'Asian', 'American Indian', 'Native Hawaiian Pacific Islander', 'Two or More Races', 'Refused During Interview']
    exp_ethn = ['Unknown', 'Hispanic or Latino', 'NOT Hispanic or Latino', 'Refused During Interview']
    date_race_eth = new_race_case_df.columns.values.tolist()[-1]
    diff = (datetime.now() - (date_race_eth)).total_seconds()/3600
    if diff > 48:
        raise Exception("Scraping Race/Ethn for wrong date - Cases")

    if len(new_race_case_df.index) != (len(exp_races) + len(exp_ethn)):
        raise Exception("More/Less Races/Ethnicities Cases: " + len(new_race_case_df.index))

    for index, row in new_race_case_df.iterrows():
        if row["Race/Ethnicity Category"] == "Race":
            if row["Race/Ethnicity Values"] not in exp_races:
                raise Exception("Unexpected Race in Race Cases")
            if row["Race/Ethnicity Values"] == "Unknown" or row["Race/Ethnicity Values"] == "Refused During Interview":
                out["# Cases Race/Ethnicity: " + row["Race/Ethnicity Values"] + " Race"] = row[date_race_eth]
            else:
                out["# Cases Race/Ethnicity: " + row["Race/Ethnicity Values"]] = row[date_race_eth]
        elif row["Race/Ethnicity Category"] == "Ethnicity":
            if row["Race/Ethnicity Values"] not in exp_ethn:
                raise Exception("Unexpected Ethn in Race Cases")
            if row["Race/Ethnicity Values"] == "Unknown" or row["Race/Ethnicity Values"] == "Refused During Interview":
                out["# Cases Race/Ethnicity: " + row["Race/Ethnicity Values"] + " Ethnicity"] = row[date_race_eth]
            else:
                out["# Cases Race/Ethnicity: " + row["Race/Ethnicity Values"]] = row[date_race_eth]

    # Add Race data - Deaths
    exp_race_ethn = ['Asian', 'Black', 'Hispanic/Latinx', 'Non-Hispanic White', 'Other']
    date_race_eth = new_race_death_df.columns.values.tolist()[-1]
    diff = (datetime.now() - (date_race_eth)).total_seconds()/3600

    if diff > 48:
        raise Exception("Scraping Race/Ethn for wrong date - Deaths")

    if len(new_race_death_df.index) != len(exp_race_ethn):
        raise Exception("More/Less Races/Ethnicities Cases: " + len(new_race_case_df.index))

    for index, row in new_race_death_df.iterrows():
        if row[0] not in exp_race_ethn:
            raise Exception("Unexpected Race/Ethn in deaths: " + row.iloc[index, 0])
        out["# Deaths Race/Ethnicity: " + row[0]] = row[date_race_eth]

    # Add testing/Hospital data
    desired = ['Total Overall Number of Tests', 'Total Residents Tested', 'Total Positives', 'Number of Deaths', 'People Recovered', 'Total ICU Beds in Hospitals', 'ICU Beds Available', 'Total Reported Ventilators in Hospitals', 'In-Use Ventilators in Hospitals', 'Ventilators Available in Hospitals', 'Total COVID-19 Patients in DC Hospitals', 'Total COVID-19 Patients in ICU']
    count = 0
    date_hosp = new_test_hosp_df.columns.values.tolist()[-1]
    diff = (datetime.now() - (date_race_eth)).total_seconds()/3600

    if diff > 48:
        raise Exception("Scraping Testing and Hosp for wrong date")

    for index, row in new_test_hosp_df.iterrows():
        if row[0] in desired:
            count += 1
            out[row[0]] = row[date_hosp]
    if count != len(desired):
        print(new_test_hosp_df)
        raise Exception("Did not scrape all of desired testing and hosp data")

    # Add scrapetime to out
    out["pullTime"] = now

    # Output
    fields = sorted([x for x in out])
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])

if __name__ == '__main__':
    run_DC({})

