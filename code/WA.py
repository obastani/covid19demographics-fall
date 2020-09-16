# https://www.doh.wa.gov/emergencies/coronavirus
# https://www.doh.wa.gov/Emergencies/COVID19/DataDashboard
import csv
from datetime import datetime
import json
import os
import re
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def makeHeader(requestID):
    return {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "c4cfc72c-5725-6c38-bb81-30777e8b6580", "RequestId": requestID, "X-PowerBI-ResourceKey": "aac255f1-9e9a-43a3-a5de-bc5adc16f09e", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"}

def run_WA(args):
    # Parameters
    raw_name = '../WA/raw'
    data_name = '../WA/data/data.csv'
    now = str(datetime.now())

    headers = {"Referer": "https://www.doh.wa.gov/Emergencies/COVID19/DataDashboard", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "Host": "www.doh.wa.gov", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", }
    dat = requests.get("https://www.doh.wa.gov/Emergencies/COVID19/DataDashboard", headers=headers)
    with open("%s/%s.html" % (raw_name, now), "w") as fp:
        fp.write(dat.text)
    
    # Selenium
    # driver = webdriver.Safari()
    driver = webdriver.Chrome(executable_path="andrew/ChromeDriver/chromedriver.exe")
    driver.maximize_window()
    driver.get("https://www.doh.wa.gov/Emergencies/COVID19/DataDashboard")
    time.sleep(10)
    
    out = {}
    out_county = []

    # County
    tbl_button = driver.find_element_by_xpath('//*[@id="togConfirmedCasesDeathsTbl"]')
    driver.execute_script("arguments[0].click();", tbl_button)
    time.sleep(5)

    tbl = driver.find_element_by_xpath('//*[@id="pnlConfirmedCasesDeathsTbl"]/div/div/table/tbody')

    driver.execute_script("arguments[0].scrollIntoView();", tbl)
    driver.save_screenshot(raw_name + "/" + now + "_county.png")

    tbl_children = tbl.find_elements_by_xpath('.//*')
    tbl_headers = tbl.find_elements_by_xpath('//*[@id="pnlConfirmedCasesDeathsTbl"]/div/div/table/thead/tr/*')
    exp_headers = ['County', 'Confirmed Cases', 'Hospitalizations', 'Deaths']

    if len(tbl_headers) != len(exp_headers):
        raise Exception("Unexpected number of fields in County table")

    for i in range(len(tbl_headers)):
        if tbl_headers[i].text != exp_headers[i]:
            print([tbl_headers[i].text, exp_headers[i]])
            raise Exception("Field names changed order in County table")

    for row in tbl_children:
        vals = row.find_elements_by_xpath('.//*')
        if vals:
            str_vals = [x.text for x in vals]
            while("" in str_vals):
                str_vals.remove("")
            if len(str_vals) == 5:
                county = {
                    "County Name": str_vals[0],
                    "Total Cases": str_vals[2].replace(",",""),
                    "Total Hospitalized": str_vals[3].replace(",",""),
                    "Total Deaths": str_vals[4].replace(",",""),
                    "Scrape Time": now,
                }
                out_county.append(county)
 
    # Tested
    try:
        tbl_button = driver.find_element_by_xpath('//*[@id="togTestingTbl"]')
        driver.execute_script("arguments[0].click();", tbl_button)
        time.sleep(2)

        tbl = driver.find_element_by_xpath('//*[@id="pnlTestingTbl"]/div/div/table/tbody')

        driver.execute_script("arguments[0].scrollIntoView();", tbl)
        driver.save_screenshot(raw_name + "/" + now + "_testing.png")

        tbl_children = tbl.find_elements_by_xpath('.//*')
        exp_headers = ["Negative", "Positive"]
        count = 0 
        for row in tbl_children:
            vals = row.find_elements_by_xpath('.//*')
            if vals:
                str_vals = [x.text for x in vals]
                while("" in str_vals):
                    str_vals.remove("")
                if len(str_vals) != 3:
                    raise Exception("Unexpected number of values in Testing Table")
                abs_val = str_vals[1]
                pct_val = str_vals[2]
                # if "%" not in pct_val:
                #     raise Exception("No % for percent value, please check - Testing Table")
                out["Total Tested: " + str_vals[0]] = abs_val.replace(",", "")
                out["% Total Tested: " + str_vals[0]] = pct_val.replace("%","")
                count += 1
        if count != len(exp_headers):
            raise Exception("Unexpected number of results in Testing Table")
        print("Testing table is back. Re-check.")
    except:
        print("No testing table still")

    # Cases, Deaths, Hosp - Age
    tbl_button = driver.find_element_by_xpath('//*[@id="togCasesDeathsByAgeTbl"]')
    driver.execute_script("arguments[0].click();", tbl_button)
    time.sleep(2)

    tbl = driver.find_element_by_xpath('//*[@id="pnlCasesDeathsByAgeTbl"]/div/div/table/tbody')

    driver.execute_script("arguments[0].scrollIntoView();", tbl)
    driver.save_screenshot(raw_name + "/" + now + "_age.png")

    tbl_children = tbl.find_elements_by_xpath('.//*')
    tbl_headers = tbl.find_elements_by_xpath('//*[@id="pnlCasesDeathsByAgeTbl"]/div/div/table/thead/tr/*')
    exp_headers = ['Age Group', 'Percent of Cases', 'Percent of Hospitalizations', 'Percent of Deaths']
    exp_ages = ["0-19", "20-39", "40-59", "60-79", "80+", "Unknown"]

    if len(tbl_headers) != len(exp_headers):
        raise Exception("Unexpected number of fields in Age table")

    for i in range(len(tbl_headers)):
        if tbl_headers[i].text != exp_headers[i]:
            print([tbl_headers[i].text, exp_headers[i]])
            raise Exception("Field names changed order in Age table")

    for row in tbl_children:
        vals = row.find_elements_by_xpath('.//*')
        if vals:
            str_vals = [x.text for x in vals]
            while("" in str_vals):
                str_vals.remove("")
            if len(str_vals) != 4:
                raise Exception("Unexpected number of values in Age table")
            if str_vals[0] not in exp_ages:
                raise Exception("Unexpected Age Group in Age table")
            out["% Cases Age [" + str_vals[0] + "]"] = str_vals[1].replace("%","")
            out["% Hospitalized Age [" + str_vals[0] + "]"] = str_vals[2].replace("%","")
            out["% Deaths Age [" + str_vals[0] + "]"] = str_vals[3].replace("%","")
  

    # Cases, Deaths, Hosp - Sex
    tbl_button = driver.find_element_by_xpath('//*[@id="togCasesDeathsByGenderTbl"]')
    driver.execute_script("arguments[0].click();", tbl_button)
    time.sleep(2)

    tbl = driver.find_element_by_xpath('//*[@id="pnlCasesDeathsByGenderTbl"]/div/div/table/tbody')

    driver.execute_script("arguments[0].scrollIntoView();", tbl)
    driver.save_screenshot(raw_name + "/" + now + "_sex.png")

    tbl_children = tbl.find_elements_by_xpath('.//*')
    tbl_headers = tbl.find_elements_by_xpath('//*[@id="pnlCasesDeathsByGenderTbl"]/div/div/table/thead/tr/*')
    exp_headers = ['Sex at Birth', 'Percent of Cases', 'Percent of Hospitalizations', 'Percent of Deaths']
    exp_sexes = ["Female", "Male", "Unknown"]

    if len(tbl_headers) != len(exp_headers):
        raise Exception("Unexpected number of fields in Sex table")

    for i in range(len(tbl_headers)):
        if tbl_headers[i].text != exp_headers[i]:
            print([tbl_headers[i].text, exp_headers[i]])
            raise Exception("Field names changed order in Sex table")

    for row in tbl_children:
        vals = row.find_elements_by_xpath('.//*')
        if vals:
            str_vals = [x.text for x in vals]
            while("" in str_vals):
                str_vals.remove("")
            if len(str_vals) != 4:
                raise Exception("Unexpected number of values in Sex table")
            if str_vals[0] not in exp_sexes:
                raise Exception("Unexpected Sex in Sex table")
            if str_vals[0] == "Unknown":
                out["% Total Cases: " + str_vals[0] + " Sex"] = str_vals[1].replace("%","")
                out["% Total Hospitalized: " + str_vals[0] + " Sex"] = str_vals[2].replace("%","")
                out["% Total Deaths: " + str_vals[0] + " Sex"] = str_vals[3].replace("%","")
            else:
                out["% Total Cases: " + str_vals[0]] = str_vals[1].replace("%","")
                out["% Total Hospitalized: " + str_vals[0]] = str_vals[2].replace("%","")
                out["% Total Deaths: " + str_vals[0]] = str_vals[3].replace("%","")

    # Cases - Race/Ethn
    tbl_button = driver.find_element_by_xpath('//*[@id="togConfirmedCasesByRaceTbl"]')
    driver.execute_script("arguments[0].click();", tbl_button)
    time.sleep(2)

    tbl = driver.find_element_by_xpath('//*[@id="pnlConfirmedCasesByRaceTbl"]/div/div/table/tbody')

    driver.execute_script("arguments[0].scrollIntoView();", tbl)
    driver.save_screenshot(raw_name + "/" + now + "_case_race.png")

    tbl_children = tbl.find_elements_by_xpath('.//*')
    tbl_headers = tbl.find_elements_by_xpath('//*[@id="pnlConfirmedCasesByRaceTbl"]/div/div/table/thead/tr/*')
    exp_headers = ['Race/Ethnicity', 'Confirmed Cases', 'Percent of Cases *\nOut of total with reported race/ethnicity', 'Percent of Total WA Population']
    # exp_headers = ['Race/Ethnicity', 'Confirmed Cases', '\n                      Percent of Cases\xa0*Out of total with reported race/ethnicity', 'Percent of Total WA Population']
    exp_race = [
                "Unknown Race/Ethnicity (Percent out of Total Cases)",
                "Hispanic",
                "Non-Hispanic American Indian or Alaska Native",
                "Non-Hispanic Asian",
                "Non-Hispanic Black",
                "Non-Hispanic White",
                "Non-Hispanic Native Hawaiian or Other Pacific Islander",
                "Non-Hispanic Multiracial",
                "Non-Hispanic Other Race",
    ]

    if len(tbl_headers) != len(exp_headers):
        raise Exception("Unexpected number of fields in Case Race table")

    for i in range(len(tbl_headers)):
        if tbl_headers[i].text != exp_headers[i]:
            print([tbl_headers[i].text, exp_headers[i]])
            raise Exception("Field names changed order in Case Race table")

    for row in tbl_children:
        vals = row.find_elements_by_xpath('.//*')
        if vals:
            str_vals = [x.text for x in vals]
            while("" in str_vals):
                str_vals.remove("")
            if "Total" in str_vals[0] and "Unknown" not in str_vals[0]:
                continue
            if len(str_vals) != 4:
                raise Exception("Unexpected number of values in Race Case table")
            if str_vals[0] not in exp_race:
                raise Exception("Unexpected Race in Race Case table")
            if "Unknown" in str_vals[0]:
                out["# Cases Race/Ethnicity: Unknown"] = str_vals[1].replace(",", "")
                out["% Cases Race/Ethnicity: Unknown"] = str_vals[2].replace("%", "")
            else:
                out["# Cases Race/Ethnicity: " + str_vals[0]] = str_vals[1].replace(",", "")
                out["% Cases Race/Ethnicity: " + str_vals[0]] = str_vals[2].replace("%", "")
            
    # Hosp - Race/Ethn
    tbl_button = driver.find_element_by_xpath('//*[@id="togHospitalizationsByRaceTbl"]')
    driver.execute_script("arguments[0].click();", tbl_button)
    time.sleep(2)

    tbl = driver.find_element_by_xpath('//*[@id="pnlHospitalizationsByRaceTbl"]/div/div/table/tbody')

    driver.execute_script("arguments[0].scrollIntoView();", tbl)
    driver.save_screenshot(raw_name + "/" + now + "_hosp_race.png")

    tbl_children = tbl.find_elements_by_xpath('.//*')
    tbl_headers = tbl.find_elements_by_xpath('//*[@id="pnlHospitalizationsByRaceTbl"]/div/div/table/thead/tr/*')
    exp_headers = ['Race/Ethnicity', 'Hospitalization Count', 'Percent of Hospitalizations *\nOut of total with reported race/ethnicity', 'Percent of Total WA Population']
    # exp_headers = ['Race/Ethnicity', 'Hospitalization Count', 'Percent of Hospitalizations\xa0* Out of total with reported race/ethnicity', 'Percent of Total WA Population']
    exp_race = [
                "Unknown Race/Ethnicity (Percent out of Total Hospitalizations)",
                "Hispanic",
                "Non-Hispanic American Indian or Alaska Native",
                "Non-Hispanic Asian",
                "Non-Hispanic Black",
                "Non-Hispanic White",
                "Non-Hispanic Native Hawaiian or Other Pacific Islander",
                "Non-Hispanic Multiracial",
                "Non-Hispanic Other Race",
    ]

    if len(tbl_headers) != len(exp_headers):
        raise Exception("Unexpected number of fields in Hosp Race table")
    
    for i in range(len(tbl_headers)):
        if tbl_headers[i].text != exp_headers[i]:
            print([tbl_headers[i].text, exp_headers[i]])
            raise Exception("Field names changed order in Hosp Race table")

    for row in tbl_children:
        vals = row.find_elements_by_xpath('.//*')
        if vals:
            str_vals = [x.text for x in vals]
            while("" in str_vals):
                str_vals.remove("")
            if "Total" in str_vals[0] and "Unknown" not in str_vals[0]:
                continue
            if len(str_vals) != 4:
                raise Exception("Unexpected number of values in Race Case table")
            if str_vals[0] not in exp_race:
                print(str_vals)
                raise Exception("Unexpected Race in Race Case table")
            if "Unknown" in str_vals[0]:
                out["# Hospitalized Race/Ethnicity: Unknown"] = str_vals[1].replace(",", "")
                out["% Hospitalized Race/Ethnicity: Unknown"] = str_vals[2].replace("%", "")
            else:
                out["# Hospitalized Race/Ethnicity: " + str_vals[0]] = str_vals[1].replace(",", "")
                out["% Hospitalized Race/Ethnicity: " + str_vals[0]] = str_vals[2].replace("%", "")
    
    # Deaths - Race/Ethn
    tbl_button = driver.find_element_by_xpath('//*[@id="togDeathsByRaceTbl"]')
    driver.execute_script("arguments[0].click();", tbl_button)
    time.sleep(2)

    tbl = driver.find_element_by_xpath('//*[@id="pnlDeathsByRaceTbl"]/div/div/table/tbody')

    driver.execute_script("arguments[0].scrollIntoView();", tbl)
    driver.save_screenshot(raw_name + "/" + now + "_death_race.png")

    tbl_children = tbl.find_elements_by_xpath('.//*')
    tbl_headers = tbl.find_elements_by_xpath('//*[@id="pnlDeathsByRaceTbl"]/div/div/table/thead/tr/*')
    exp_headers = ['Race/Ethnicity', 'Deaths', 'Percent of Deaths *\nOut of total with reported race/ethnicity', 'Percent of Total WA Population']
    # exp_headers = ['Race/Ethnicity', 'Deaths', '\n                      Percent of Deaths\xa0*Out of total with reported race/ethnicity', 'Percent of Total WA Population']
    exp_race = [
                "Unknown Race/Ethnicity (Percent out of Total Deaths)",
                "Hispanic",
                "Non-Hispanic American Indian or Alaska Native",
                "Non-Hispanic Asian",
                "Non-Hispanic Black",
                "Non-Hispanic White",
                "Non-Hispanic Native Hawaiian or Other Pacific Islander",
                "Non-Hispanic Multiracial",
                "Non-Hispanic Other Race",
    ]

    if len(tbl_headers) != len(exp_headers):
        raise Exception("Unexpected number of fields in Death Race table")

    for i in range(len(tbl_headers)):
        if tbl_headers[i].text != exp_headers[i]:
            print([tbl_headers[i].text, exp_headers[i]])
            raise Exception("Field names changed order in Death Race table")

    for row in tbl_children:
        vals = row.find_elements_by_xpath('.//*')
        if vals:
            str_vals = [x.text for x in vals]
            while("" in str_vals):
                str_vals.remove("")
            if "Total" in str_vals[0] and "Unknown" not in str_vals[0]:
                continue
            if len(str_vals) != 4:
                raise Exception("Unexpected number of values in Race Death table")
            if str_vals[0] not in exp_race:
                print(str_vals)
                raise Exception("Unexpected Race in Race Death table")
            if "Unknown" in str_vals[0]:
                out["# Deaths Race/Ethnicity: Unknown"] = str_vals[1].replace(",", "")
                out["% Deaths Race/Ethnicity: Unknown"] = str_vals[2].replace("%", "")
            else:
                out["# Deaths Race/Ethnicity: " + str_vals[0]] = str_vals[1].replace(",", "")
                out["% Deaths Race/Ethnicity: " + str_vals[0]] = str_vals[2].replace("%", "")

    # Out
    out["Scrape_Time"] = now
    data_county = '../WA/data/data_county.csv'
    fields = sorted([x for x in out])
    exists = os.path.exists(data_name)
    with open(data_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])
    # Output - county
    for county in out_county:
        fields = sorted([x for x in county])
        exists = os.path.exists(data_county)
        with open(data_county, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([county[x] for x in fields])


def run_WA_INPROGRESS(args):
    # Parameters
    raw_name = '../WA/raw'
    statedata_name = '../WA/data/data_state.csv'
    tsdata_name = '../WA/data/data_ts.csv'
    now = str(datetime.now())
    url = "https://df-msit-scus-api.analysis.windows.net/public/reports/querydata?synchronous=true"
    out = {}

    # Grab all "data as of" responses
    paramList = [{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"p","Entity":"PULL_DoH_datetimestamp"},{"Name":"_","Entity":"_types"},{"Name":"_1","Entity":"_counties_US_only"}],"Select":[{"Measure":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"_titledatetimestamp"},"Name":"PULL_DoH_datetimestamp._titledatetimestamp"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Label"}}],"Values":[[{"Literal":{"Value":"'Confirmed cases'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}],[{"Literal":{"Value":"'Total tests'"}}],[{"Literal":{"Value":"'Negative tests'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"p\",\"Entity\":\"PULL_DoH_datetimestamp\"},{\"Name\":\"_\",\"Entity\":\"_types\"},{\"Name\":\"_1\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"p\"}},\"Property\":\"_titledatetimestamp\"},\"Name\":\"PULL_DoH_datetimestamp._titledatetimestamp\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Label\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed cases'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}],[{\"Literal\":{\"Value\":\"'Deaths'\"}}],[{\"Literal\":{\"Value\":\"'Total tests'\"}}],[{\"Literal\":{\"Value\":\"'Negative tests'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Top\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"e946b816-4696-4c56-9cdd-cf814ad91fba","Sources":[{"ReportId":"0c8d6d24-477b-4ac8-b400-d9a583b48499"}]}}],"cancelQueries":[],"modelId":2829462}]
    headerList = [makeHeader(x) for x in ["b7af67dd-70e6-92de-9638-420753ccfcfc"]]
    res = [requests.post(url, json=pp, headers=hh).json() for pp, hh in zip(paramList, headerList)]
    for idx in range(len(res)):
        with open("%s/updateTime%d_%s.json" % (raw_name, idx, now), "w") as fp:
            json.dump(res[idx], fp)
    msgs = [x["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"] for x in res]
    if not all([x == msgs[0] for x in msgs]):
        raise Exception("Not all 'as of' dates the same for WA")
    out["UpdateTime"] = str(datetime.strptime(msgs[0], "Data as of %B %d, %Y %I:%M%p PT"))

    paramList = [{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"DoH_Reportdate_combined"},{"Name":"_","Entity":"_types"},{"Name":"_1","Entity":"_counties_US_only"}],"Select":[{"Measure":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"_labelxofy"},"Name":"DoH_combined._labelxofy"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Label"}}],"Values":[[{"Literal":{"Value":"'Confirmed cases'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}],[{"Literal":{"Value":"'Total tests'"}}],[{"Literal":{"Value":"'Negative tests'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"d\",\"Entity\":\"DoH_Reportdate_combined\"},{\"Name\":\"_\",\"Entity\":\"_types\"},{\"Name\":\"_1\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"_labelxofy\"},\"Name\":\"DoH_combined._labelxofy\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Label\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed cases'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}],[{\"Literal\":{\"Value\":\"'Deaths'\"}}],[{\"Literal\":{\"Value\":\"'Total tests'\"}}],[{\"Literal\":{\"Value\":\"'Negative tests'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Top\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"e946b816-4696-4c56-9cdd-cf814ad91fba","Sources":[{"ReportId":"0c8d6d24-477b-4ac8-b400-d9a583b48499"}]}}],"cancelQueries":[],"modelId":2829462}]
    headerList = [makeHeader(x) for x in ["fe602524-bafa-3989-102e-415d23d4ae3c"]]
    res = [requests.post(url, json=pp, headers=hh).json() for pp, hh in zip(paramList, headerList)]
    for idx in range(len(res)):
        with open("%s/confNoCounty%d_%s.json" % (raw_name, idx, now), "w") as fp:
            json.dump(res[idx], fp)
    msgs = [x["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"] for x in res]
    if not all([x == msgs[0] for x in msgs]):
        raise Exception("Not all 'cases without assigned county' messages the same")
    reCounty = re.compile("(\d+) of (\d+) confirmed cases do not have an assigned county")
    match = reCounty.match(msgs[0].replace(",", ""))
    if not match:
        print(msgs[0])
        raise Exception("Unexpected 'cases without assigned county' messages")
    out["CasesWithoutAssignedCounty"] = match.group(1)
    out["TotalCases"] = match.group(2)

    paramList = [{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"DoH_Reportdate_combined"},{"Name":"_","Entity":"_types"},{"Name":"_1","Entity":"_counties_US_only"}],"Select":[{"Measure":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"_labelxofyandeath"},"Name":"DoH_combined._labelxofyandeath"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Label"}}],"Values":[[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"QueryId":"","ApplicationContext":{"DatasetId":"26590dc6-1cde-490a-b01d-334c5de5ef28","Sources":[{"ReportId":"2743d2f0-d71a-4f32-ada6-b1f0e3b863c3"}]}}],"cancelQueries":[],"modelId":2829476},
                 {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"DoH_Reportdate_combined"},{"Name":"_","Entity":"_types"},{"Name":"_1","Entity":"_counties_US_only"}],"Select":[{"Measure":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"_labelxofyandeath"},"Name":"DoH_Reportdate_combined._labelxofyandeath"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Label"}}],"Values":[[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0],"Subtotal":1}]},"DataReduction":{"DataVolume":3,"Primary":{"Window":{"Count":500}}},"Version":1}}}]},"QueryId":"","ApplicationContext":{"DatasetId":"ba9f4372-6d09-42a8-b5ef-aa8554ae6e48","Sources":[{"ReportId":"d4d78b1d-198c-4e35-8661-92c2cfe0d5b4"}]}}],"cancelQueries":[],"modelId":2829455}]
    headerList = [{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "b4b9f517-8584-4b8d-87fa-b735dbf6cdd8", "RequestId": "f0451c9a-507d-76d6-230a-f7aaa1178ae1", "X-PowerBI-ResourceKey": "18a805b5-0e9c-4e6a-930b-19fd95ccc444", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"},
                  {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "813129cc-0803-4f9b-9f8c-7f277a38b8c0", "RequestId": "cf88c1eb-e35a-d85d-d0a6-f5ea5afbe3ff", "X-PowerBI-ResourceKey": "bfae80f5-04fc-4005-9893-4eb9288cdfee", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"}]
    res = [requests.post(url, json=pp, headers=hh).json() for pp, hh in zip(paramList, headerList)]
    for idx in range(len(res)):
        with open("%s/deathNoCounty%d_%s.json" % (raw_name, idx, now), "w") as fp:
            json.dump(res[idx], fp)
    msgs = [x["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"] for x in res]
    if not all([x == msgs[0] for x in msgs]):
        raise Exception("Not all 'deaths without assigned county' messages the same")
    reCounty = re.compile("(\d+) of (\d+) deaths do not have an assigned county.")
    match = reCounty.match(msgs[0].replace(",", ""))
    if not match:
        print(msgs[0])
        raise Exception("Unexpected 'deaths without assigned county' messages")
    out["DeathsWithoutAssignedCounty"] = match.group(1)
    out["TotalDeaths"] = match.group(2)

    paramList = [{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"DoH_Reportdate_combined"},{"Name":"_","Entity":"_types"},{"Name":"_1","Entity":"_counties_US_only"}],"Select":[{"Measure":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"_labelxofyandeath2"},"Name":"DoH_Reportdate_combined._labelxofyandeath2"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Label"}}],"Values":[[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"d\",\"Entity\":\"DoH_Reportdate_combined\"},{\"Name\":\"_\",\"Entity\":\"_types\"},{\"Name\":\"_1\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"_labelxofyandeath2\"},\"Name\":\"DoH_Reportdate_combined._labelxofyandeath2\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Label\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Deaths'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}],[{\"Literal\":{\"Value\":\"'Deaths'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Top\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"26590dc6-1cde-490a-b01d-334c5de5ef28","Sources":[{"ReportId":"2743d2f0-d71a-4f32-ada6-b1f0e3b863c3"}]}}],"cancelQueries":[],"modelId":2829476},
                 {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"DoH_Reportdate_combined"},{"Name":"_","Entity":"_types"},{"Name":"_1","Entity":"_counties_US_only"}],"Select":[{"Measure":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"_labelxofyandeath2"},"Name":"DoH_Reportdate_combined._labelxofyandeath2"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Label"}}],"Values":[[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0],"Subtotal":1}]},"DataReduction":{"DataVolume":3,"Primary":{"Window":{"Count":500}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"d\",\"Entity\":\"DoH_Reportdate_combined\"},{\"Name\":\"_\",\"Entity\":\"_types\"},{\"Name\":\"_1\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"_labelxofyandeath2\"},\"Name\":\"DoH_Reportdate_combined._labelxofyandeath2\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Label\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Deaths'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}],[{\"Literal\":{\"Value\":\"'Deaths'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0],\"Subtotal\":1}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Window\":{\"Count\":500}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"ba9f4372-6d09-42a8-b5ef-aa8554ae6e48","Sources":[{"ReportId":"d4d78b1d-198c-4e35-8661-92c2cfe0d5b4"}]}}],"cancelQueries":[],"modelId":2829455}]
    headerList = [{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "b4b9f517-8584-4b8d-87fa-b735dbf6cdd8", "RequestId": "b9f88945-8055-2c32-0dc3-915cf1fe9707", "X-PowerBI-ResourceKey": "18a805b5-0e9c-4e6a-930b-19fd95ccc444", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"},
                  {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "813129cc-0803-4f9b-9f8c-7f277a38b8c0", "RequestId": "e061c854-6e96-8685-9397-1ac4903e6c52", "X-PowerBI-ResourceKey": "bfae80f5-04fc-4005-9893-4eb9288cdfee", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"}]
    res = [requests.post(url, json=pp, headers=hh).json() for pp, hh in zip(paramList, headerList)]
    for idx in range(len(res)):
        with open("%s/deathNoDOD%d_%s.json" % (raw_name, idx, now), "w") as fp:
            json.dump(res[idx], fp)
    msgs = [x["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"] for x in res]
    if not all([x == msgs[0] for x in msgs]):
        raise Exception("Not all 'deaths without DOD' messages the same")
    reDOD = re.compile("(\d+) deaths do not have a date of death available.")
    match = reDOD.match(msgs[0].replace(",", ""))
    if not match:
        print(msgs[0])
        raise Exception("Unexpected 'deaths without DOD' messages")
    out["DeathsWithoutAssignedDOD"] = match.group(1)
    
    params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"DoH_Reportdate_combined"},{"Name":"_","Entity":"_typesfordemo"},{"Name":"_1","Entity":"_counties_US_only"}],"Select":[{"Arithmetic":{"Left":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"value"}},"Function":0}},"Right":{"ScopedEval":{"Expression":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"value"}},"Function":0}},"Scope":[]}},"Operator":3},"Name":"Sum(DoH_combined.value)"},{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"_type gender"},"Name":"DoH_combined.type gender"},{"Measure":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"DemoTitleSex"},"Name":"_typesfordemo.DemoTitleSex"}],"Where":[{"Condition":{"Not":{"Expression":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"_type gender"}}],"Values":[[{"Literal":{"Value":"null"}}]]}}}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type_demographics"}}],"Values":[[{"Literal":{"Value":"'Confirmed cases'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}},{"Condition":{"Not":{"Expression":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type_demographics"}}],"Values":[[{"Literal":{"Value":"null"}}]]}}}}}],"OrderBy":[{"Direction":2,"Expression":{"Arithmetic":{"Left":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"value"}},"Function":0}},"Right":{"ScopedEval":{"Expression":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"value"}},"Function":0}},"Scope":[]}},"Operator":3}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1]}]},"Projections":[2],"DataReduction":{"DataVolume":4,"Primary":{"Window":{"Count":1000}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"d\",\"Entity\":\"DoH_Reportdate_combined\"},{\"Name\":\"_\",\"Entity\":\"_typesfordemo\"},{\"Name\":\"_1\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Arithmetic\":{\"Left\":{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"value\"}},\"Function\":0}},\"Right\":{\"ScopedEval\":{\"Expression\":{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"value\"}},\"Function\":0}},\"Scope\":[]}},\"Operator\":3},\"Name\":\"Sum(DoH_combined.value)\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"_type gender\"},\"Name\":\"DoH_combined.type gender\"},{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"DemoTitleSex\"},\"Name\":\"_typesfordemo.DemoTitleSex\"}],\"Where\":[{\"Condition\":{\"Not\":{\"Expression\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"_type gender\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"null\"}}]]}}}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"type_demographics\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed cases'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}},{\"Condition\":{\"Not\":{\"Expression\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"type_demographics\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"null\"}}]]}}}}}],\"OrderBy\":[{\"Direction\":2,\"Expression\":{\"Arithmetic\":{\"Left\":{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"value\"}},\"Function\":0}},\"Right\":{\"ScopedEval\":{\"Expression\":{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"value\"}},\"Function\":0}},\"Scope\":[]}},\"Operator\":3}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0,1]}]},\"Projections\":[2],\"DataReduction\":{\"DataVolume\":4,\"Primary\":{\"Window\":{\"Count\":1000}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"e7dfdf5d-81cc-4146-b286-ac6c5931114c","Sources":[{"ReportId":"4d8d1978-4340-464f-a645-58f82409739e"}]}}],"cancelQueries":[],"modelId":2829447}
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "58145414-a5be-016f-ea3b-7ce7f838b57f", "RequestId": "f9f03525-acf9-66c5-a166-82ae14e9f208", "X-PowerBI-ResourceKey": "8751808f-633f-48b0-a98e-26c8ba3f59d8", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"}
    gender = requests.post(url, json=params, headers=headers).json()
    with open("%s/gender_%s.json" % (raw_name, now), "w") as fp:
        json.dump(gender, fp)
    genderdat = gender["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    genderlabs = [x["C"][0] for x in genderdat]
    gendervals = [float(x["C"][1]) for x in genderdat]
    if sorted(genderlabs) != ["Female", "Male", "Unknown"]:
        raise("Unexpected gender labels")
    for lab, val in zip(genderlabs, gendervals):
        out["CasesPropGender" + lab] = val

    params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"DoH_Reportdate_combined"},{"Name":"_","Entity":"_typesfordemo"},{"Name":"_1","Entity":"_counties_US_only"}],"Select":[{"Arithmetic":{"Left":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"value"}},"Function":0}},"Right":{"ScopedEval":{"Expression":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"value"}},"Function":0}},"Scope":[]}},"Operator":3},"Name":"Divide(Sum(DoH_combined.value), ScopedEval(Sum(DoH_combined.value), []))"},{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"_agegroupgroup2"},"Name":"DoH_combined._agegroupgroup2"},{"Measure":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"DemoTitleAge"},"Name":"_typesfordemo.DemoTitleAge"}],"Where":[{"Condition":{"Not":{"Expression":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"_agegroupgroup2"}}],"Values":[[{"Literal":{"Value":"null"}}]]}}}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type_demographics"}}],"Values":[[{"Literal":{"Value":"'Confirmed cases'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}},{"Condition":{"Not":{"Expression":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type_demographics"}}],"Values":[[{"Literal":{"Value":"null"}}]]}}}}}],"OrderBy":[{"Direction":1,"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"_agegroupgroup2"}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1]}]},"Projections":[2],"DataReduction":{"DataVolume":4,"Primary":{"Window":{"Count":1000}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"d\",\"Entity\":\"DoH_Reportdate_combined\"},{\"Name\":\"_\",\"Entity\":\"_typesfordemo\"},{\"Name\":\"_1\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Arithmetic\":{\"Left\":{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"value\"}},\"Function\":0}},\"Right\":{\"ScopedEval\":{\"Expression\":{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"value\"}},\"Function\":0}},\"Scope\":[]}},\"Operator\":3},\"Name\":\"Divide(Sum(DoH_combined.value), ScopedEval(Sum(DoH_combined.value), []))\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"_agegroupgroup2\"},\"Name\":\"DoH_combined._agegroupgroup2\"},{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"DemoTitleAge\"},\"Name\":\"_typesfordemo.DemoTitleAge\"}],\"Where\":[{\"Condition\":{\"Not\":{\"Expression\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"_agegroupgroup2\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"null\"}}]]}}}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"type_demographics\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed cases'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}},{\"Condition\":{\"Not\":{\"Expression\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"type_demographics\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"null\"}}]]}}}}}],\"OrderBy\":[{\"Direction\":1,\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"_agegroupgroup2\"}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0,1]}]},\"Projections\":[2],\"DataReduction\":{\"DataVolume\":4,\"Primary\":{\"Window\":{\"Count\":1000}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"e7dfdf5d-81cc-4146-b286-ac6c5931114c","Sources":[{"ReportId":"4d8d1978-4340-464f-a645-58f82409739e"}]}}],"cancelQueries":[],"modelId":2829447}
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "58145414-a5be-016f-ea3b-7ce7f838b57f", "RequestId": "b59a4af0-5a36-3e70-1e2a-ca4c1ef22e49", "X-PowerBI-ResourceKey": "8751808f-633f-48b0-a98e-26c8ba3f59d8", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"}
    age = requests.post(url, json=params, headers=headers).json()
    with open("%s/age_%s.json" % (raw_name, now), "w") as fp:
        json.dump(age, fp)
    agedat = age["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    agelabs = [x["C"][0] for x in agedat]
    agevals = [float(x["C"][1]) for x in agedat]
    if sorted(agelabs) != ["00-19", "20-39", "40-59", "60-79", "80+"]:
        raise("Unexpected age labels")
    for lab, val in zip(agelabs, agevals):
        out["CasesPropAge_" + lab.replace("-", "_").replace("00", "0").replace("+", "_plus")] = val

    params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"_","Entity":"_counties_US_only"},{"Name":"_1","Entity":"_types"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Confirmed"}},"Function":0},"Name":"Sum(_counties_US_only.Confirmed)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Deaths"}},"Function":0},"Name":"Sum(_counties_US_only.Deaths)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Total tests"}},"Function":0},"Name":"Sum(_counties_US_only.Total tests)"},{"Measure":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"_percentpos"},"Name":"_counties_US_only._percentpos"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}],[{"Literal":{"Value":"'Total tests'"}}],[{"Literal":{"Value":"'Negative tests'"}}]]}}}],"OrderBy":[{"Direction":2,"Expression":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Confirmed"}},"Function":0}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1,2,3]}]},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"_\",\"Entity\":\"_counties_US_only\"},{\"Name\":\"_1\",\"Entity\":\"_types\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Confirmed\"}},\"Function\":0},\"Name\":\"Sum(_counties_US_only.Confirmed)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Deaths\"}},\"Function\":0},\"Name\":\"Sum(_counties_US_only.Deaths)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Total tests\"}},\"Function\":0},\"Name\":\"Sum(_counties_US_only.Total tests)\"},{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"_percentpos\"},\"Name\":\"_counties_US_only._percentpos\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}],[{\"Literal\":{\"Value\":\"'Deaths'\"}}],[{\"Literal\":{\"Value\":\"'Total tests'\"}}],[{\"Literal\":{\"Value\":\"'Negative tests'\"}}]]}}}],\"OrderBy\":[{\"Direction\":2,\"Expression\":{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Confirmed\"}},\"Function\":0}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0,1,2,3]}]},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"e946b816-4696-4c56-9cdd-cf814ad91fba","Sources":[{"ReportId":"0c8d6d24-477b-4ac8-b400-d9a583b48499"}]}}],"cancelQueries":[],"modelId":2829462}
    headers = makeHeader("5329b55f-046c-c1fd-eb55-dc8e5d44e798")
    simple = requests.post(url, json=params, headers=headers).json()
    with open("%s/simple_%s.json" % (raw_name, now), "w") as fp:
        json.dump(simple, fp)
    simpledat = simple["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["C"]
    out["PositiveTests"] = int(simpledat[0])
    out["Deaths"] = int(simpledat[1])
    out["TotalTests"] = int(simpledat[2])
        
    paramList = [{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"c","Entity":"CDC_Event_Date"},{"Name":"_","Entity":"_types"},{"Name":"_1","Entity":"_dates"},{"Name":"_2","Entity":"_counties_US_only"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"c"}},"Property":"value"}},"Function":0},"Name":"Sum(CDC_Event_Date.value)"},{"Column":{"Expression":{"SourceRef":{"Source":"c"}},"Property":"Date"},"Name":"CDC_Event_Date.Date"},{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Label"},"Name":"_types.Label"}],"Where":[{"Condition":{"Comparison":{"ComparisonKind":2,"Left":{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"Date"}},"Right":{"DateSpan":{"Expression":{"Literal":{"Value":"datetime'2020-02-28T00:00:00'"}},"TimeUnit":5}}}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Label"}}],"Values":[[{"Literal":{"Value":"'Confirmed cases'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_2"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1]}]},"Secondary":{"Groupings":[{"Projections":[2]}]},"DataReduction":{"DataVolume":4,"Primary":{"Sample":{}},"Secondary":{"Top":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"c\",\"Entity\":\"CDC_Event_Date\"},{\"Name\":\"_\",\"Entity\":\"_types\"},{\"Name\":\"_1\",\"Entity\":\"_dates\"},{\"Name\":\"_2\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"c\"}},\"Property\":\"value\"}},\"Function\":0},\"Name\":\"Sum(CDC_Event_Date.value)\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"c\"}},\"Property\":\"Date\"},\"Name\":\"CDC_Event_Date.Date\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Label\"},\"Name\":\"_types.Label\"}],\"Where\":[{\"Condition\":{\"Comparison\":{\"ComparisonKind\":2,\"Left\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"Date\"}},\"Right\":{\"DateSpan\":{\"Expression\":{\"Literal\":{\"Value\":\"datetime'2020-02-28T00:00:00'\"}},\"TimeUnit\":5}}}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Label\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed cases'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}],[{\"Literal\":{\"Value\":\"'Deaths'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_2\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0,1]}]},\"Secondary\":{\"Groupings\":[{\"Projections\":[2]}]},\"DataReduction\":{\"DataVolume\":4,\"Primary\":{\"Sample\":{}},\"Secondary\":{\"Top\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"26590dc6-1cde-490a-b01d-334c5de5ef28","Sources":[{"ReportId":"2743d2f0-d71a-4f32-ada6-b1f0e3b863c3"}]}}],"cancelQueries":[],"modelId":2829476},
                 {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"_1","Entity":"_types"},{"Name":"d","Entity":"DoH_Reportdate_combined"},{"Name":"_","Entity":"_dates"},{"Name":"_11","Entity":"_counties_US_only"}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"type"},"Name":"_types.type"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"cumulative"}},"Function":0},"Name":"Sum(doh_combined.cumulative)"},{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Date"},"Name":"_dates.Date"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_11"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[1,2]}]},"Secondary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":4,"Intersection":{"BinnedLineSample":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"_1\",\"Entity\":\"_types\"},{\"Name\":\"d\",\"Entity\":\"DoH_Reportdate_combined\"},{\"Name\":\"_\",\"Entity\":\"_dates\"},{\"Name\":\"_11\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"type\"},\"Name\":\"_types.type\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"cumulative\"}},\"Function\":0},\"Name\":\"Sum(doh_combined.cumulative)\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Date\"},\"Name\":\"_dates.Date\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}],[{\"Literal\":{\"Value\":\"'Deaths'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_11\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[1,2]}]},\"Secondary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":4,\"Intersection\":{\"BinnedLineSample\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"ba9f4372-6d09-42a8-b5ef-aa8554ae6e48","Sources":[{"ReportId":"d4d78b1d-198c-4e35-8661-92c2cfe0d5b4"}]}}],"cancelQueries":[],"modelId":2829455},
                 {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"c","Entity":"CDC_Event_Date"},{"Name":"_","Entity":"_types"},{"Name":"_1","Entity":"_dates"},{"Name":"_2","Entity":"_counties_US_only"}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"c"}},"Property":"value"}},"Function":0},"Name":"Sum(CDC_Event_Date.value)"},{"Column":{"Expression":{"SourceRef":{"Source":"c"}},"Property":"Date"},"Name":"CDC_Event_Date.Date"},{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Label"},"Name":"_types.Label"}],"Where":[{"Condition":{"Comparison":{"ComparisonKind":2,"Left":{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"Date"}},"Right":{"DateSpan":{"Expression":{"Literal":{"Value":"datetime'2020-02-28T00:00:00'"}},"TimeUnit":5}}}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Label"}}],"Values":[[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_2"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1]}]},"Secondary":{"Groupings":[{"Projections":[2]}]},"DataReduction":{"DataVolume":4,"Primary":{"Sample":{}},"Secondary":{"Top":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"c\",\"Entity\":\"CDC_Event_Date\"},{\"Name\":\"_\",\"Entity\":\"_types\"},{\"Name\":\"_1\",\"Entity\":\"_dates\"},{\"Name\":\"_2\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"c\"}},\"Property\":\"value\"}},\"Function\":0},\"Name\":\"Sum(CDC_Event_Date.value)\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"c\"}},\"Property\":\"Date\"},\"Name\":\"CDC_Event_Date.Date\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Label\"},\"Name\":\"_types.Label\"}],\"Where\":[{\"Condition\":{\"Comparison\":{\"ComparisonKind\":2,\"Left\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"Date\"}},\"Right\":{\"DateSpan\":{\"Expression\":{\"Literal\":{\"Value\":\"datetime'2020-02-28T00:00:00'\"}},\"TimeUnit\":5}}}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Label\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Deaths'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}],[{\"Literal\":{\"Value\":\"'Deaths'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_2\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0,1]}]},\"Secondary\":{\"Groupings\":[{\"Projections\":[2]}]},\"DataReduction\":{\"DataVolume\":4,\"Primary\":{\"Sample\":{}},\"Secondary\":{\"Top\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"26590dc6-1cde-490a-b01d-334c5de5ef28","Sources":[{"ReportId":"2743d2f0-d71a-4f32-ada6-b1f0e3b863c3"}]}}],"cancelQueries":[],"modelId":2829476},
    {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"_1","Entity":"_types"},{"Name":"d","Entity":"DoH_Reportdate_combined"},{"Name":"_11","Entity":"_counties_US_only"}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"type"},"Name":"_types.type"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"cumulative"}},"Function":0},"Name":"Sum(doh_combined.cumulative)"},{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"date"},"Name":"DoH_combined.date"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Confirmed'"}}],[{"Literal":{"Value":"'Deaths'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_11"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[1,2]}]},"Secondary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":4,"Intersection":{"BinnedLineSample":{}}},"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"_1\",\"Entity\":\"_types\"},{\"Name\":\"d\",\"Entity\":\"DoH_Reportdate_combined\"},{\"Name\":\"_11\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"type\"},\"Name\":\"_types.type\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"cumulative\"}},\"Function\":0},\"Name\":\"Sum(doh_combined.cumulative)\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"date\"},\"Name\":\"DoH_combined.date\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Deaths'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Confirmed'\"}}],[{\"Literal\":{\"Value\":\"'Deaths'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_11\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[1,2]}]},\"Secondary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":4,\"Intersection\":{\"BinnedLineSample\":{}}},\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"ba9f4372-6d09-42a8-b5ef-aa8554ae6e48","Sources":[{"ReportId":"d4d78b1d-198c-4e35-8661-92c2cfe0d5b4"}]}}],"cancelQueries":[],"modelId":2829455}]
    headerList = [{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "086cbf8b-1fc7-fe25-6da8-104a2342be17", "RequestId": "4d193b2c-f391-dbd6-e3ce-60e8d4871faf", "X-PowerBI-ResourceKey": "18a805b5-0e9c-4e6a-930b-19fd95ccc444", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"},
                  {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "bfdc4aba-cd8b-12ac-202b-a7cd7fa475a7", "RequestId": "19bc822f-d00a-82ce-fd00-5862bd4b013d", "X-PowerBI-ResourceKey": "bfae80f5-04fc-4005-9893-4eb9288cdfee", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"},
                  {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "b4b9f517-8584-4b8d-87fa-b735dbf6cdd8", "RequestId": "f9df095d-7274-9b8a-a1cd-9f0152cdcc8b", "X-PowerBI-ResourceKey": "18a805b5-0e9c-4e6a-930b-19fd95ccc444", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"},
                  {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "813129cc-0803-4f9b-9f8c-7f277a38b8c0", "RequestId": "7afa8f22-b124-5a3e-3778-2243b5296eee", "X-PowerBI-ResourceKey": "bfae80f5-04fc-4005-9893-4eb9288cdfee", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"}]
    byday = {}  # Date -> [cases by onset, cases by report, deaths by onset, deaths by report, positive tests by collection date, negative tests by collection date]
    for idx in range(len(paramList)):
        rec = requests.post(url, json=paramList[idx], headers=headerList[idx]).json()
        with open("%s/TS%d_%s.json" % (raw_name, idx, now), "w") as fp:
            json.dump(rec, fp)
        skip = 0
        for x in rec["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]:
            if "G0" in x:
                dt = datetime.utcfromtimestamp(x["G0"]/1000).strftime("%Y-%m-%d")
                if not dt in byday:
                    byday[dt] = [None] * 6
                if "M0" in x["X"][0]:
                    byday[dt][idx] = int(x["X"][0]["M0"])
                elif "R" not in x["X"][0] or x["X"][0]["R"] != 1:
                    raise Exception("Unexpected structure in by-day data")
            else:
                skip += 1
        if skip > 1:
            raise Exception("Too many skipped rows in by-day data")

    params = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"p","Entity":"PULL_Tests_Specimen_Collect"},{"Name":"_","Entity":"_dates"},{"Name":"_1","Entity":"_daterange_select"},{"Name":"_2","Entity":"_types"},{"Name":"_3","Entity":"_counties_US_only"}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"Date"},"Name":"PULL_Tests_Specimen_Collect.Date"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"NewPos"}},"Function":0},"Name":"Sum(PULL_Tests_Specimen_Collect.NewPos)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"NewNeg"}},"Function":0},"Name":"Sum(PULL_Tests_Specimen_Collect.NewNeg)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"Total tests"}},"Function":0},"Name":"Sum(PULL_Tests_Specimen_Collect.Total tests)"},{"Measure":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"_percposspecimen"},"Name":"PULL_Tests_Specimen_Collect._percposspecimen"}],"Where":[{"Condition":{"Comparison":{"ComparisonKind":2,"Left":{"Column":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Date"}},"Right":{"DateSpan":{"Expression":{"Literal":{"Value":"datetime'2020-02-28T00:00:00'"}},"TimeUnit":5}}}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_1"}},"Property":"Date_range"}}],"Values":[[{"Literal":{"Value":"'All dates'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_2"}},"Property":"type"}}],"Values":[[{"Literal":{"Value":"'Positive tests'"}}],[{"Literal":{"Value":"'Negative tests'"}}],[{"Literal":{"Value":"'Confirmed'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"_3"}},"Property":"State Name"}}],"Values":[[{"Literal":{"Value":"'Washington'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1,2,3,4]}]},"DataReduction":{"DataVolume":4,"Primary":{"Sample":{}}},"SuppressedJoinPredicates":[3,4],"Version":1}}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"p\",\"Entity\":\"PULL_Tests_Specimen_Collect\"},{\"Name\":\"_\",\"Entity\":\"_dates\"},{\"Name\":\"_1\",\"Entity\":\"_daterange_select\"},{\"Name\":\"_2\",\"Entity\":\"_types\"},{\"Name\":\"_3\",\"Entity\":\"_counties_US_only\"}],\"Select\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"p\"}},\"Property\":\"Date\"},\"Name\":\"PULL_Tests_Specimen_Collect.Date\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"p\"}},\"Property\":\"NewPos\"}},\"Function\":0},\"Name\":\"Sum(PULL_Tests_Specimen_Collect.NewPos)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"p\"}},\"Property\":\"NewNeg\"}},\"Function\":0},\"Name\":\"Sum(PULL_Tests_Specimen_Collect.NewNeg)\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"p\"}},\"Property\":\"Total tests\"}},\"Function\":0},\"Name\":\"Sum(PULL_Tests_Specimen_Collect.Total tests)\"},{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"p\"}},\"Property\":\"_percposspecimen\"},\"Name\":\"PULL_Tests_Specimen_Collect._percposspecimen\"}],\"Where\":[{\"Condition\":{\"Comparison\":{\"ComparisonKind\":2,\"Left\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_\"}},\"Property\":\"Date\"}},\"Right\":{\"DateSpan\":{\"Expression\":{\"Literal\":{\"Value\":\"datetime'2020-02-28T00:00:00'\"}},\"TimeUnit\":5}}}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_1\"}},\"Property\":\"Date_range\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'All dates'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_2\"}},\"Property\":\"type\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Positive tests'\"}}],[{\"Literal\":{\"Value\":\"'Negative tests'\"}}],[{\"Literal\":{\"Value\":\"'Confirmed'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"_3\"}},\"Property\":\"State Name\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Washington'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0,1,2,3,4]}]},\"DataReduction\":{\"DataVolume\":4,\"Primary\":{\"Sample\":{}}},\"SuppressedJoinPredicates\":[3,4],\"Version\":1}}}]}","QueryId":"","ApplicationContext":{"DatasetId":"8e220d38-a0e9-4e35-a4e8-6fdd408a9447","Sources":[{"ReportId":"43f067bb-37c3-4ff3-91cb-0ca4d0dcaf2f"}]}}],"cancelQueries":[],"modelId":2829444}
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36", "ActivityId": "81af639d-e61a-e623-a2a5-fdf2e076fd78", "RequestId": "e1ac1ff1-8d77-5b76-476c-158ce751dfb2", "X-PowerBI-ResourceKey": "75b62661-cb0d-4d6d-bbfa-4d230745e7e7", "Origin": "https://msit.powerbi.com", "Referer": "https://msit.powerbi.com/view?r=eyJrIjoiYmZhZTgwZjUtMDRmYy00MDA1LTk4OTMtNGViOTI4OGNkZmVlIiwidCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsImMiOjV9"}
    testing = requests.post(url, json=params, headers=headers).json()
    with open("%s/testing_%s.json" % (raw_name, now), "w") as fp:
        json.dump(testing, fp)
    for x in testing["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]:
        dt = datetime.utcfromtimestamp(x["C"][0]/1000).strftime("%Y-%m-%d")
        if not dt in byday:
            byday[dt] = [None] * 6
        byday[dt][4] = int(x["C"][1])
        byday[dt][5] = int(x["C"][2])

    # Output
    out["Scrape_Time"] = now
    fields = sorted([x for x in out])
    exists = os.path.exists(statedata_name)
    with open(statedata_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(fields)
        writer.writerow([out[x] for x in fields])
    exists = os.path.exists(tsdata_name)
    with open(tsdata_name, "a") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(["CasesByOnsetDate", "CumCasesByReportDate", "DeathsByOnsetDate", "CumDeathsByDOD", "PosTestsByCollectDate", "NegTestsByCollectDate",
                             "TimeSeriesDate", "UpdateDate", "Scrape_Time"])
        days = sorted([x for x in byday])
        for dt in days:
            writer.writerow(byday[dt] + [dt, out["UpdateTime"], now])

if __name__ == '__main__':
    run_WA({})
