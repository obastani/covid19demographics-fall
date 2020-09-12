import os
from datetime import datetime, timedelta
import time

to_ignore = ['AK', 'GU', 'OH', 'PR', 'SC', 'WI', 'MA', 'NC', 'OK', 'TN']

for folder in os.listdir("../"):
    if folder in to_ignore:
        continue
    elif folder == "CA":
        files = ['data_age.csv', 'data_county.csv', 'data_race.csv', 'data_sex.csv', 'data_testing.csv', 'hospital_data.csv']
        for file in files:
            last_modified = os.stat("../" + folder + "/data/" + file).st_mtime
            diff = time.time() - last_modified
            if diff > 1123200:
                print(folder + " last updated: " + str(datetime.fromtimestamp(last_modified)) + "for " + file)
    elif folder == "CT":
        files = ['data_age.csv', 'data_county.csv', 'data_county_testing.csv', 'data_gender.csv', 'data_race.csv']
        for file in files:
            last_modified = os.stat("../" + folder + "/data/" + file).st_mtime
            diff = time.time() - last_modified
            if diff > 1123200:
                print(folder + " last updated: " + str(datetime.fromtimestamp(last_modified)) + "for " + file)
    elif folder == "MS":
        files = ['data_cases.csv', 'data_deaths.csv']
        for file in files:
            last_modified = os.stat("../" + folder + "/data/" + file).st_mtime
            diff = time.time() - last_modified
            if diff > 1123200:
                print(folder + " last updated: " + str(datetime.fromtimestamp(last_modified)) + "for " + file)
    elif folder == "MT":
        files = ['data_case.csv', 'data_county.csv', 'data_state.csv']
        for file in files:
            last_modified = os.stat("../" + folder + "/data/" + file).st_mtime
            diff = time.time() - last_modified
            if diff > 1123200:
                print(folder + " last updated: " + str(datetime.fromtimestamp(last_modified)) + "for " + file)
    elif folder == "VA":
        files = ['data_age.csv', 'data_conf.csv', 'data_dist.csv', 'data_locality.csv', 'data_race_ethnicity.csv', 'data_sex.csv']
        for file in files:
            last_modified = os.stat("../" + folder + "/data/" + file).st_mtime
            diff = time.time() - last_modified
            if diff > 1123200:
                print(folder + " last updated: " + str(datetime.fromtimestamp(last_modified)) + "for " + file)
        # print([str(file) for file in os.listdir("../" + folder + "/data/")])
        # exit()
    elif folder == "WV":
        files = ['data_county.csv']
        for file in files:
            last_modified = os.stat("../" + folder + "/data/" + file).st_mtime
            diff = time.time() - last_modified
            if diff > 1123200:
                print(folder + " last updated: " + str(datetime.fromtimestamp(last_modified)))
    elif len(folder) == 2 or folder == "Iceland" or folder == "SouthKorea":
        if os.path.exists("../" + folder + "/data/data.csv"):
            last_modified = os.stat("../" + folder + "/data/data.csv").st_mtime
            diff = time.time() - last_modified
            if diff > 1123200:
                print(folder + " last updated: " + str(datetime.fromtimestamp(last_modified)))
        else:
            print("No data.csv in " + folder)

        if os.path.exists("../" + folder + "/data/data_county.csv"):
            last_modified = os.stat("../" + folder + "/data/data_county.csv").st_mtime
            diff = time.time() - last_modified
            if diff > 1123200:
                print(folder + " county last updated: " + str(datetime.fromtimestamp(last_modified)))

        