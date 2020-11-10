import os
import requests
import pandas as pd
from datetime import datetime
import json
import csv

def export(vec, data_name):
    for row in vec:
        fields = sorted([x for x in row])
        exists = os.path.exists(data_name)
        with open(data_name, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([row[x] for x in fields])

def get_most_recent(data_file):
    if os.path.exists(data_file):
        dates = pd.read_csv(data_file)["Reported Date"].tolist()
        dt_dates = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in dates]
        most_recent = max(dt for dt in dt_dates if dt < datetime.now())
        return most_recent
    else:
        filename = ""
        count = 1
        exists = True
        while exists:
            filename = data_file.replace(".csv", "_V" + str(count) + ".csv")
            count += 1
            exists = os.path.exists(data_file.replace(".csv", "_V" + str(count) + ".csv"))
        dates = pd.read_csv(filename)["Reported Date"].tolist()
        dt_dates = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in dates]
        most_recent = max(dt for dt in dt_dates if dt < datetime.now())
        return most_recent

def run_CT(args):
    # day, month, year = args['day'], args['month'], args['year']
    # cmd = 'curl https://portal.ct.gov/-/media/Coronavirus/CTDPHCOVID19summary{}{}20{}.pdf > ../CT/raw/{}-{}-{}.pdf'.format(month, day, year, month, day, year)
    # os.system(cmd)

    # Parameters
    raw_name = "../CT/raw"
    now = str(datetime.now())

    # Output
    data_age = "../CT/data/data_age.csv"
    data_gender = "../CT/data/data_gender.csv"
    data_race = "../CT/data/data_race.csv"
    data_county_testing = "../CT/data/data_county_testing.csv"
    data_county_all = "../CT/data/data_county.csv"

    # Links
    county_tests = "https://data.ct.gov/resource/qfkt-uahj.json"
    county_summary = "https://data.ct.gov/resource/bfnu-rgqt.json"
    statewide_summary = "https://data.ct.gov/resource/rf3k-f8fg.json"
    gender_table = "https://data.ct.gov/resource/qa53-fghg.json"
    race_ethn = "https://data.ct.gov/resource/7rne-efic.json"
    age_table = "https://data.ct.gov/resource/ypz6-8qyf.json"

    # Get raw
    county_tests_json =  ["/" + now + "_county_tests.json", requests.get(county_tests).json()]
    county_summary_json = ["/" + now + "_county_summary.json", requests.get(county_summary).json()]
    statewide_summary_json = ["/" + now + "_statewide.json", requests.get(statewide_summary).json()]
    gender_json = ["/" + now + "_gender.json", requests.get(gender_table).json()]
    race_ethn_json = ["/" + now + "_race_ethn.json", requests.get(race_ethn).json()]
    age_json = ["/" + now + "_age.json", requests.get(age_table).json()]

    files = [county_tests_json, county_summary_json, statewide_summary_json, gender_json, race_ethn_json, age_json]

    # Save Raw
    for file in files:
        with open(raw_name + file[0], "w") as fp:
            json.dump(file[1], fp)

    # County 
    out_county = []
    most_recent = get_most_recent(data_county_all)
    for row in county_summary_json[1]:
        # print(row)
        date = datetime.strptime(row["dateupdated"], "%Y-%m-%dT%H:%M:%S.%f")
        if date <= most_recent:
            continue
        print("Most recently collected: " + str(most_recent))
        print("Available to collect: " + str(date))
        county = row["county"]
        try: 
            val_conf = row["confirmedcases"]
        except:
            val_conf = None
        try: 
            val_prob = row["probablecases"]
        except:
            val_prob = None
        try: 
            dval_conf = row["confirmeddeaths"]
        except:
            dval_conf = None
        try: 
            dval_prob = row["probabledeaths"]
        except:
            dval_prob = None
        county = {
                    "County Name": county,
                    "Reported Date": str(date),
                    "Total Cases": row["totalcases"],
                    "Total Confirmed Cases": val_conf,
                    "Total Probable Cases": val_prob,
                    "Total Hospitalized": row["hospitalization"],
                    "Total Deaths": row["totaldeaths"],
                    "Total Confirmed Deaths": dval_conf,
                    "Total Probable Deaths": dval_prob
                }
        out_county.append(county)
    
    # Testing data - skipping pending and 7/11
    out_testing_county = []
    most_recent = get_most_recent(data_county_testing)
    for row in county_tests_json[1]:
        date = datetime.strptime(row["date"], "%Y-%m-%dT%H:%M:%S.%f")
        if date <= most_recent:
            continue
        print("Most recently collected: " + str(most_recent))
        print("Available to collect: " + str(date))
        county = row["county"]
        county = {
            "County Name": county,
            "Reported Date": str(date),
            "Total Tested: PCR" : row["number_of_pcr_tests"],
            "Total Positive Tested: PCR" : row["number_of_pcr_positives"],
            "Total Negative Tested: PCR" : row["number_of_pcr_negatives"],
            "Total Indeterminates Tested: PCR" : row["number_of_pcr_indeterminates"],
            "Total Tested: AG" : row["number_of_ag_tests"],
            "Total Positive Tested: AG" : row["number_of_ag_positives"],
            "Total Negative Tested: AG" : row["number_of_ag_negatives"],
            "Total Indeterminates Tested: AG" : row["number_of_ag_indeterminates"],
        }
        out_testing_county.append(county)
    

    # Statewide data
    out_gender = {}
    out_race = {}
    out_age = {}

    # Gender
    most_recent = get_most_recent(data_gender)
    for row in gender_json[1]:
        date = datetime.strptime(row["dateupdated"], "%Y-%m-%dT%H:%M:%S.%f")
        if date <= most_recent:
            continue
        print("Most recently collected: " + str(most_recent))
        print("Available to collect: " + str(date))
        gender = row["gender"]
        try: 
            val_conf = row["confirmedcases"]
        except:
            val_conf = None
        try: 
            val_prob = row["probablecases"]
        except:
            val_prob = None
        try: 
            dval_conf = row["confirmeddeaths"]
        except:
            dval_conf = None
        try: 
            dval_prob = row["probabledeaths"]
        except:
            dval_prob = None
        try:
            deaths = row["totaldeaths"]
        except:
            deaths = None
        if str(date) not in out_gender:
            out_gender[str(date)] = {
                "Total Cases: " + gender: row["totalcases"],
                "Total Probable Cases: " + gender: val_prob,
                "Total Confirmed Cases: " + gender: val_conf,
                "Total Deaths: " + gender: deaths,
                "Total Confirmed Deaths: " + gender: dval_conf,
                "Total Probable Deaths: " + gender: dval_prob,

            }
        else:
            out_gender[str(date)]["Total Cases: " + gender] = row["totalcases"]
            out_gender[str(date)]["Total Probable Cases: " + gender] = val_prob
            out_gender[str(date)]["Total Confirmed Cases: " + gender] = val_conf
            out_gender[str(date)]["Total Deaths: " + gender] = deaths
            out_gender[str(date)]["Total Confirmed Deaths: " + gender] = dval_conf
            out_gender[str(date)]["Total Probable Deaths: " + gender] = dval_prob
    
    # Race
    most_recent = get_most_recent(data_race)
    for row in race_ethn_json[1]:
        date = datetime.strptime(row["dateupdated"], "%Y-%m-%dT%H:%M:%S.%f")
        if date <= most_recent:
            continue
        print("Most recently collected: " + str(most_recent))
        print("Available to collect: " + str(date))
        race_ethn = row["hisp_race"]
        if race_ethn == "Unknown":
            race_ethn = "Unknown Race"
        if str(date) not in out_race:
            out_race[str(date)] = {}
        out_race[str(date)]["# Cases Race/Ethnicity: " + race_ethn] = row["case_tot"]
        out_race[str(date)]["# Deaths Race/Ethnicity: " + race_ethn] = row["deaths"]

    # Age
    most_recent = get_most_recent(data_age)
    for row in age_json[1]:
        date = datetime.strptime(row["dateupdated"], "%Y-%m-%dT%H:%M:%S.%f")
        if date <= most_recent:
            continue
        print("Most recently collected: " + str(most_recent))
        print("Available to collect: " + str(date))
        age = row["agegroups"]
        try: 
            val_conf = row["confirmedcases"]
        except:
            val_conf = None
        try: 
            val_prob = row["probablecases"]
        except:
            val_prob = None
        try: 
            dval_conf = row["confirmeddeaths"]
        except:
            dval_conf = None
        try: 
            dval_prob = row["probabledeaths"]
        except:
            dval_prob = None
        try:
            deaths = row["totaldeaths"]
        except:
            deaths = None
        if str(date) not in out_age:
            out_age[str(date)] = {}
        out_age[str(date)]["# Cases Age [" + age + "]"] = row["totalcases"]
        out_age[str(date)]["# Confirmed Cases Age [" + age + "]"] = val_conf
        out_age[str(date)]["# Probable Cases Age [" + age + "]"] = val_prob
        out_age[str(date)]["# Deaths Age [" + age + "]"] = deaths
        out_age[str(date)]["# Confirmed Deaths Age [" + age + "]"] = dval_conf 
        out_age[str(date)]["# Probable Deaths Age [" + age + "]"] = dval_prob

    # Output - Age
    vec = []
    for day in out_age:
        out_age[day]["Reported Date"] = day
        vec.append(out_age[day])

    export(vec, data_age)

    # Output - Gender
    vec = []
    for day in out_gender:
        out_gender[day]["Reported Date"] = day
        vec.append(out_gender[day])

    export(vec, data_gender)

    # Output - Race
    vec = []
    for day in out_race:
        out_race[day]["Reported Date"] = day
        vec.append(out_race[day])

    export(vec, data_race)

    # Output - County Testing
    export(out_testing_county, data_county_testing)

    # Output - County
    export(out_county, data_county_all)
    
if __name__ == '__main__':
    run_CT({})
