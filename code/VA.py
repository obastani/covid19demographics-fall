# http://www.vdh.virginia.gov/coronavirus/

from bs4 import BeautifulSoup
import csv
from datetime import datetime
from io import StringIO
import os
import requests
import pandas as pd

# Remove empty rows
def filtered(rows):
    return [x for x in rows if "".join([(x[y] or "").strip() for y in x]) != ""]

def run_VA(args):
    # Parameters
    raw_name = '../VA/raw'
    data_name = '../VA/data/data_%s.csv'
    now = datetime.now()

    links  = [("locality", "https://data.virginia.gov/resource/bre9-aqqr.csv"),
              ("conf", "https://data.virginia.gov/resource/uqs3-x7zh.csv"),
              ("dist", "https://data.virginia.gov/resource/v5a8-4ahw.csv"),
              ("age", "https://data.virginia.gov/resource/uktn-mwig.csv"),
              ("sex", "https://data.virginia.gov/resource/tdt3-q47w.csv"),
              ("race_ethnicity", "https://data.virginia.gov/resource/9sba-m86n.csv")]

    for link in links:
        most_recent = ""
        exists = os.path.exists(data_name % link[0])
        out = []
        
        # If current data file does not exist
        if not exists:
            version = 0
            v_exists = True
            while v_exists:
                version += 1
                v_exists = os.path.exists((data_name % (link[0] + "_V" + str(version))))
            version = version - 1
            v_df = pd.read_csv((data_name % (link[0] + "_V" + str(version))))
            date_col = ""
            for col in v_df.columns:
                if "date" in col.lower() and "report" in col.lower():
                    date_col = col
                    break
            # Getting most recent date
            dates = (pd.to_datetime(v_df[date_col])).to_list()
            most_recent = max(dt for dt in dates if dt < now)

            # Getting new dates
            new_df = pd.read_csv(link[1])
            new_df.to_csv(raw_name + "/" + link[0] + "_" + str(now) + ".csv")
            new_date_col = ""
            for col in new_df.columns:
                if "date" in col.lower() and "report" in col.lower():
                    new_date_col = col
                    break
            new_df[new_date_col] = pd.to_datetime(new_df[new_date_col])
            rows = new_df.to_dict(orient="records")
            for row in rows:
                if row[new_date_col] <= most_recent:
                    continue
                else:
                    out.append(row)
        else:
            curr_df = pd.read_csv(data_name % link[0])
            date_col = ""
            for col in curr_df.columns:
                if "date" in col.lower() and "report" in col.lower():
                    date_col = col
                    break
            # Getting most recent date
            dates = (pd.to_datetime(curr_df[date_col])).to_list()
            most_recent = max(dt for dt in dates if dt < now)

            # Getting new dates
            new_df = pd.read_csv(link[1])
            new_df.to_csv(raw_name + "/" + link[0] + "_" + str(now) + ".csv")
            new_date_col = ""
            for col in new_df.columns:
                if "date" in col.lower() and "report" in col.lower():
                    new_date_col = col
                    break
            new_df[new_date_col] = pd.to_datetime(new_df[new_date_col])
            new_df_cols = sorted([x for x in new_df.columns])
            cur_df_cols = sorted([x for x in curr_df.columns])
            if len(new_df_cols) != len(cur_df_cols):
                raise Exception("Unexpected number of columns for " + link[0])
            # Checking order and columns are the same
            for col1, col2 in zip(new_df_cols, cur_df_cols):
                if col1 != col2:
                    raise Exception("Unexpected column order for " + link[0])
            
            rows = new_df.to_dict(orient="records")
            for row in rows:
                if row[new_date_col] <= most_recent:
                    continue
                else:
                    out.append(row)
        # Output
        for row in out:
            fields = sorted([x for x in row])
            exists = os.path.exists(data_name % link[0])
            with open(data_name % link[0], "a") as fp:
                writer = csv.writer(fp)
                if not exists:
                    writer.writerow(fields)
                writer.writerow([row[x] for x in fields])



        # curr_df = pd.read_csv(data_name % link[0])
        # new_df = pd.read_csv(link[1])
        # print(curr_df)
        # print(new_df)

    ###################

    # r = requests.get("http://www.vdh.virginia.gov/coronavirus/", verify=False).text
    # with open("%s/%s.html" % (raw_name, now), "w") as fp:
    #     fp.write(r)
    # soup = BeautifulSoup(r, "html.parser")
    # links = soup.find_all("a")
    # localitylink = [x for x in links if "cases" in x.text.lower() and not "by" in x.text.lower()]
    # conflink = [x for x in links if "cases" in x.text.lower() and "confirmation" in x.text.lower()]
    # distlink = [x for x in links if "cases" in x.text.lower() and "district" in x.text.lower()]
    # agelink = [x for x in links if "cases" in x.text.lower() and "age" in x.text.lower()]
    # sexlink = [x for x in links if "cases" in x.text.lower() and "sex" in x.text.lower()]
    # # racelink = [x for x in links if "cases" in x.text.lower() and ("race" in x.text.lower() and "race-ethnicity" not in x.text.lower())]
    # # ethlink = [x for x in links if "cases" in x.text.lower() and ("ethnicity" in x.text.lower() and "race-ethnicity" not in x.text.lower())]
    # raceethlink = [x for x in links if "cases" in x.text.lower() and "race-ethnicity" in x.text.lower()]
    # edatelink = [x for x in links if "eventdate" in x.text.lower()]

    # if len([x for x in links if "cases" in x.text.lower()]) != 6 or len(edatelink) != 1:
    #     raise Exception("Unexpected number of cases links")
    
    # files = [(localitylink, "locality", ["Report Date", "FIPS", "Locality", "VDH Health District", "Total Cases", "Hospitalizations", "Deaths"]),
    #          (conflink, "conf", ["Report Date", "Case Status", "Number of Cases", "Number of Hospitalizations", "Number of Deaths"]),
    #          (distlink, "dist", ["Report Date", "Health District", "Number of Cases", "Number of Hospitalizations", "Number of Deaths"]),
    #          (agelink, "age", ["Health District", "Report Date", "Age Group", "Number of Cases", "Number of Hospitalizations", "Number of Deaths"]),
    #          (sexlink, "sex", ["Health District", "Report Date", "Sex", "Number of Cases", "Number of Hospitalizations", "Number of Deaths"]),
    #         #  (racelink, "race", ["Health District", "Report Date", "Race", "Number of Cases", "Number of Hospitalizations", "Number of Deaths"]),
    #         #  (ethlink, "ethnicity", ["Report Date", "Health District", "Ethnicity", "Number of Cases", "Number of Hospitalizations", "Number of Deaths"]),
    #          (raceethlink, "race_ethnicity", ["Report Date", "Health District or Health District Group", "Race and Ethnicity", "Number of Cases", "Number of Hospitalizations", "Number of Deaths"])]
    # for link, name, fields in files:
    #     print(link)
    #     continue
    #     if len(link) != 1:
    #         raise Exception("Malformed link for type " + name)
    #     thiscsv = requests.get(link[0]["href"], verify=False).text
    #     with open("%s/%s_%s.csv" % (raw_name, name, now), "w") as fp:
    #         fp.write(thiscsv)
    #     thisdat = filtered([x for x in csv.DictReader(StringIO(thiscsv))])
    #     if len(thisdat) == 0:
    #         raise Exception("No data for type " + name)
    #     if len(thisdat[0]) != len(fields) or not all([x in thisdat[0] for x in fields]):
    #         raise Exception("Bad fields for type " + name + " -- " + str([x for x in thisdat[0]]))
    #     fields = fields + ["Scrape_Time"]
    #     exists = os.path.exists(data_name % name)
    #     with open(data_name % name, "a") as fp:
    #         writer = csv.writer(fp)
    #         if not exists:
    #             writer.writerow(fields)
    #         for xx in thisdat:
    #             xx["Scrape_Time"] = now
    #             writer.writerow([xx[x] for x in fields])
    # exit()
    # edatecsv = requests.get(edatelink[0]["href"], verify=False).text
    # with open("%s/edate_%s.csv" % (raw_name, now), "w") as fp:
    #     fp.write(edatecsv)

if __name__ == '__main__':
    run_VA({})

