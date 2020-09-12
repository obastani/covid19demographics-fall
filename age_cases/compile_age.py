import pandas as pd
import os
import csv
from datetime import datetime
import json
import gzip

path2json = "covid19demographics/data/"
states =  [
    "AL",
    "AR",
    "CA",
    "CO",
    "CT",
    "DC",
    "DE",
    "FL",
    "GA",
    "IA",
    "ID",
    "IL",
    "IN",
    "LA",
    "MA",
    "MD",
    "ME",
    "MI",
    "MN",
    "MO",
    "MT",
    "NC",
    "ND",
    "NV",
    "NY",
    "OK",
    "OR",
    "PA",
    "RI",
    "SD",
    "SouthKorea",
    "TN",
    "TX",
    "UT",
    "VA",
    "WA",
    "WY"
]

# Get filename
filename = ""
for file in os.listdir(path2json):
    filename = file

# Read file to python
with gzip.GzipFile(path2json + filename, 'r') as fin:
    data = json.loads(fin.read().decode('utf-8'))

# Iterate through each folder
out = {}
for region in data:
    for state in data[region]:
        if state not in states:
            continue
        out_list = []
        for row in data[region][state]:
            headers = [x for x in row]
            for col in row:
                if "Cases Age" in col:
                    try:
                        time = row["Report Date"]
                    except:
                        try:
                            time = row["Reported Date"]
                        except:
                            try:
                                time = row["Reported Date"]
                            except:
                                try:
                                    time = row["Scrape Time"]
                                except:
                                    print([x for x in row])
                                    print("No time " + state)
                                    raise
                    converted = False
                    value = row[col]
                    if "%" in col:
                        try:
                            value = row[col]/100 * row["Total Cases"]
                            converted = True
                            print("Converted % to Abs: " + state)
                        except:
                            print("Unable to convert % to Abs: " + state)
                    columns_name = ""
                    if converted:
                        column_name = col.replace("%", "#")
                    else:
                        column_name = col
                    if "County Name" in headers:
                            new_row = {
                                "State": state,
                                "County": row["County Name"],
                                "Column Name": column_name,
                                "Value": value,
                                "Scrape Time": time
                            }
                    else:
                        new_row = {
                            "State": state,
                            "Column Name": column_name,
                            "Value": value,
                            "Scrape Time": time
                        }
                    out_list.append(new_row)
        out[state] = out_list

# Export
for state in out:
    data = "age_cases" + "/" + state + ".csv"
    for new_row in out[state]:
        fields = sorted([x for x in new_row])
        exists = os.path.exists(data)
        with open(data, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([new_row[x] for x in fields])
        
    # region_data = data[region]
    # print(region)
    # for state in region_data:
    #     print(state)
    #     if state in states:
    #         try:
    #             out = []
    #             for row in data[str(region)][str(state)]:
    #                 for col in row:
    #                     if "Cases Age" in col:
    #                         try:
    #                             time = row["Report Date"]
    #                         except:
    #                             try:
    #                                 time = row["Report Time"]
    #                             except:
    #                                 time = row["Scrape Time"]
    #                         new_row = {
    #                             "State": state,
    #                             "Column Name": col,
    #                             "Value": row[col],
    #                             "Scrape Time": time
    #                         }
    #                         out.append(new_row)
    #             # Output
    #             data = "age_cases" + "/" + state + ".csv"
    #             for new_row in out:
    #                 fields = sorted([x for x in new_row])
    #                 exists = os.path.exists(data)
    #                 with open(data, "a") as fp:
    #                     writer = csv.writer(fp)
    #                     if not exists:
    #                         writer.writerow(fields)
    #                     writer.writerow([new_row[x] for x in fields])
    #         except:
    #             print("Unable to compile: " + state)

