# It appears that they have started making Google sheets available, but only for 3/27 so far. We need to monitor how they make the file available in the future to automate the scraping process.

# Following https://pythonhosted.org/PyDrive/quickstart.html
# Step 1: go to https://console.developers.google.com/iam-admin/projects; left side
# "APIs & Services" -> "Credentials". Click "Create Credentials"; "OAuth client ID"
# "Web application". Enter http://localhost:8080 for the authorized Javascript
# origins and the Authorized Redirect URIs.
# For me, create yields:
# Client ID 1078053222972-c6ntsosqqbc7epbkt42jvj9mhslr248i.apps.googleusercontent.com
# Secret VC0PNf2d4r2f5yfBbPoO0ABx
# Now click the download next to your new credential (probably called "Web client 1")
# Move the downloaded file to this folder and name it client_secrets.json .

import csv
from datetime import datetime
from io import StringIO
import os
import pandas as pd
import pydrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import re

def run_CO(args):
    # Parameters
    raw_name = '../CO/raw'
    data_name = '../CO/data/data.csv'
    now = str(datetime.now())

    # Get a list of files in the public google drive for CO
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Loads up "client_secrets.json"
    drive = GoogleDrive(gauth)
    fileid = '1bBAC7H-pdEDgPxRuU_eR36ghzc0HWNf1'
    # https://drive.google.com/drive/folders/1bBAC7H-pdEDgPxRuU_eR36ghzc0HWNf1
    filelist = drive.ListFile({'q': "'%s' in parents and trashed=false" % fileid}).GetList()
    fdat = [(x["id"], x["title"]) for x in filelist if "covid19_case_summary" in x["title"]]

    # Get last date
    try:
        data_df = pd.read_csv(data_name)
    except:
        count = 0
        for file in os.listdir('../CO/data/'):
            count += 1
        data_df = pd.read_csv('../CO/data/dataV' + str(count) + ".csv")
    dates = data_df["FileDate"].tolist()
    last_date = datetime.strptime(dates[-1], "%Y-%m-%d")

    # Download any files we don't have
    toprocess = []
    for fid, title in fdat:
        cname = "%s/%s" % (raw_name, title)
        if not os.path.exists(cname):
            try:
                file_date = datetime.strptime((title.replace('.csv', '')).replace("covid19_case_summary_", ""), "%Y-%m-%d")
            except:
                print("Change in file names. Check.")
                raise
            # Get files that are newer than our last date
            if file_date > last_date:
                if ".csv" in title:
                    fp = drive.CreateFile({"id": fid})
                    content = fp.GetContentString()
                    with open(cname, "w") as fout:
                        fout.write(content)
                    toprocess.append((content, title))
                else:
                    raise Exception("Warning: new file not in csv format --> Check!")

    # Process any new files -- 4-tuple of (description, attribute, metric, our name)
    grabs = [("State Data", "Statewide", "Cases", "Total Cases"),
             ("State Data", "Statewide", "Hospitalizations", "Total Hospitalized"),
             ("State Data", "Statewide", "People Tested", "Total Tested"),
             ("State Data", "Statewide", "Deaths", "Total Deaths"),
             ("State Data", "Statewide", "Outbreaks", "# Outbreaks"),
             ("COVID-19 in Colorado by Sex", "Male", "Percent of Cases", "% Total Cases: Male"),
             ("COVID-19 in Colorado by Sex", "Female", "Percent of Cases", "% Total Cases: Female"),
             ("COVID-19 in Colorado by Sex", "Unknown", "Percent of Cases", "% Total Cases: Unknown Sex"),
             ("COVID-19 in Colorado by Race & Ethnicity", "AIAN - Non Hispanic", "Percent of Cases", "% Cases Race/Ethnicity: AIAN - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Asian - Non Hispanic", "Percent of Cases", "% Cases Race/Ethnicity: Asian - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Black - Non Hispanic", "Percent of Cases", "% Cases Race/Ethnicity: Black - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Hispanic, All Races", "Percent of Cases", "% Cases Race/Ethnicity: Hispanic, All Races"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Multiple - Non Hispanic", "Percent of Cases", "% Cases Race/Ethnicity: Multiple - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "NHOPI - Non Hispanic", "Percent of Cases", "% Cases Race/Ethnicity: NHOPI - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "White - Non Hispanic", "Percent of Cases", "% Cases Race/Ethnicity: White - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Other", "Percent of Cases", "% Cases Race/Ethnicity: Other"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Unknown/Not Provided", "Percent of Cases", "% Cases Race/Ethnicity: Unknown/Not Provided"),
             ("COVID-19 in Colorado by Race & Ethnicity", "AIAN - Non Hispanic", "Percent of Deaths", "% Deaths Race/Ethnicity: AIAN - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Asian - Non Hispanic", "Percent of Deaths", "% Deaths Race/Ethnicity: Asian - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Black - Non Hispanic", "Percent of Deaths", "% Deaths Race/Ethnicity: Black - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Hispanic, All Races", "Percent of Deaths", "% Deaths Race/Ethnicity: Hispanic, All Races"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Multiple - Non Hispanic", "Percent of Deaths", "% Deaths Race/Ethnicity: Multiple - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "NHOPI - Non Hispanic", "Percent of Deaths", "% Deaths Race/Ethnicity: NHOPI - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "White - Non Hispanic", "Percent of Deaths", "% Deaths Race/Ethnicity: White - Non Hispanic"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Other", "Percent of Deaths", "% Deaths Race/Ethnicity: Other"),
             ("COVID-19 in Colorado by Race & Ethnicity", "Unknown/Not Provided", "Percent of Deaths", "% Deaths Race/Ethnicity: Unknown/Not Provided"),
             
            ]
            #  ("Fatal cases by sex", "Female", "Cases", "GenderFemaleDeaths"),
            #  ("Fatal cases by sex", "Male", "Cases", "GenderMaleDeaths")]
    for rng in ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80+", "Unknown"]:
        grabs.append(("COVID-19 in Colorado by Age Group", rng, "Percent of Cases", "% Cases Age [" + rng + "]"))
        grabs.append(("COVID-19 in Colorado by Age Group", rng, "Percent of Deaths", "% Deaths Age [" + rng + "]"))
        grabs.append(("Cases of COVID-19 Reported in Colorado by Age Group, Hospitalization, and Outcome", rng + ", Not Hospitalized", "Cases", "# Not Hospitalized Age [" + rng + "]"))
        grabs.append(("Cases of COVID-19 Reported in Colorado by Age Group, Hospitalization, and Outcome", rng + ", Hospitalized", "Cases", "# Hospitalized Age [" + rng + "]"))
        grabs.append(("Cases of COVID-19 Reported in Colorado by Age Group, Hospitalization, and Outcome", rng + ", Deaths", "Cases", "# Deaths Age [" + rng + "]"))
    grabMap = {x[:3]: x[3] for x in grabs}  # (desc, attr, metric) -> our name
    fields = sorted([x[3] for x in grabs]) + ["FileDate", "Scrape Time"]

    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        for content, title in toprocess:
            out = {x[3]: None for x in grabs}
            reader = csv.DictReader(StringIO(content))
            for line in reader:
                key = (line["description"], line["attribute"], line["metric"])
                if key in grabMap:
                    out[grabMap[key]] = float(line["value"])
            # Not sure if this works. If breaks, get Andrew
            # if count != len(grabMap):
            #     print(count, len(grabMap))
                # raise Exception("Unable to get all desired data. Check that description, attribute and metric all match in the raw file")
            match = re.compile(r"(\d\d\d\d-\d\d-\d\d)").search(title)
            if not match:
                raise Exception("Invalid file name: " + title)
            out["FileDate"] = match.group(1)
            out["Scrape Time"] = now
            # Check
            expected_null = ["# Deaths Age [0-9]", "# Deaths Age [Unknown]", "% Deaths Age [0-9]", "% Deaths Age [Unknown]", "Total Deaths", "# Hospitalized Age [Unknown]"]
            for key in out:
                if not out[key]:
                    print("Warning: Null Value for " + key)
                    if key not in expected_null:
                        raise Exception("Null Value for " + key)
                    elif key != "Total Deaths":
                        out[key] = 0
            writer.writerow([out[x] for x in fields])

if __name__ == '__main__':
    run_CO({})
