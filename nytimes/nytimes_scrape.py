from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import re
import sys
from urllib.request import urlopen, Request
import re
import os
import pandas as pd

# Example inputs:
# About 39.6 million people
# About 293,000 people
def getPop(x):
    spl = x.split()
    if spl[0] == "About" and spl[2] == "million" and spl[3] == "people":
        return int(float(spl[1]) * 1000000)
    elif spl[0] == "About" and spl[2] == "people":
        return int(spl[1].replace(",", ""))
    else:
        print("Unexpected population:", x)
        exit(0)

# Get order type and effective date/time
def getInfo(x):
    if x.span.text.find(", effective ") != 0:
        print("Unexpected order info format:", x)
        exit(0)
    dateText = x.span.text[12:].replace(".", "").replace("am", "AM").replace("pm", "PM")
    if dateText.find(" at ") < 0:
        dateText += " at 12 AM"
    if dateText.find(":") >= 0:
        dt = datetime.strptime("2020 " + dateText, "%Y %B %d at %I:%M %p")
    else:
        dt = datetime.strptime("2020 " + dateText, "%Y %B %d at %I %p")
    return x.find(text=True), dt

# Given place-wrap div, return place, pop, order, dt, orderLink, newsLink
def getPlace(x):
    placeP = x.find("p", class_="l-place")
    if placeP is not None:
        place = placeP.find(text=True).strip()
    else:
        place = None
    popSpan = x.find("span", class_="l-population", recursive=True)
    if popSpan is not None:
        pop = getPop(popSpan.text)
    else:
        pop = None
    order, dt = getInfo(x.find("p", class_="l-order"))
    orderSpan = x.find("span", class_="linkorder", recursive=True)
    if orderSpan is not None:
        orderLink = orderSpan.find("a")["href"]
    else:
        orderLink = None
    newsSpan = x.find("span", class_="linklocalnews", recursive=True)
    if newsSpan is not None:
        newsLink = newsSpan.find("a")["href"]
    else:
        newsLink = None
    return place, pop, order, dt, orderLink, newsLink

def scrape():
    data = "nytimes.csv"
    dates = pd.read_csv(data)["Report Date"]
    dates = set(dates.unique())
    # Get last updated
    url = "https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url=url, headers=headers) 
    html = urlopen(req).read() 
    soup = BeautifulSoup(html, "html.parser")
    last_updated = (soup.find("time", class_="css-wcxsge").text).replace("Updated", "").strip()
    if last_updated in dates:
        print("Already collected most recent data for nytimes")
    else:
        rows = []
        print("Getting data for " + last_updated)
        # Getting each status div
        try:
            reopened = ("Reopened", (soup.find("div", class_="g-list-container g-cat-reopened")).find_all("div", class_="g-state g-cat-reopened"))
        except:
            try:
                reopened = ("Reopened", (soup.find("div", class_="g-list-container g-cat-reopened")).find_all("div", class_="g-state g-cat-reopened "))
            except:
                reopened = ("",[])
        try:
            forward = ("Forward", (soup.find("div", class_="g-list-container g-cat-forward")).find_all("div", class_="g-state g-cat-forward"))
        except:
            try:
                forward = ("Forward", (soup.find("div", class_="g-list-container g-cat-forward")).find_all("div", class_="g-state g-cat-forward "))
            except:
                forward = ("",[])
        try:
            pausing = ("Pausing", (soup.find("div", class_="g-list-container g-cat-pausing")).find_all("div", class_="g-state g-cat-pausing"))
        except:
            try:
                pausing = ("Pausing", (soup.find("div", class_="g-list-container g-cat-pausing")).find_all("div", class_="g-state g-cat-pausing "))
            except:
                pausing = ("",[])
        try:
            reversing = ("Reversing", (soup.find("div", class_="g-list-container g-cat-reversing")).find_all("div", class_="g-state g-cat-reversing"))
        except:
            try:
                reversing = ("Reversing", (soup.find("div", class_="g-list-container g-cat-reversing")).find_all("div", class_="g-state g-cat-reversing "))
            except:
                reversing = ("",[])
        try:
            reopening = ("Reopening", (soup.find("div", class_="g-list-container g-cat-reopening")).find_all("div", class_="g-state g-cat-reopening"))
        except:
            try:
                reopening = ("Reopening", (soup.find("div", class_="g-list-container g-cat-reopening")).find_all("div", class_="g-state g-cat-reopening "))
            except:
                reopening = ("",[])
        try:
            soon = ("Order Lifting or Reopening in the Next Week", (soup.find("div", class_="g-list-container g-cat-soon")).find_all("div", class_="g-state g-cat-soon"))
        except:
            try:
                soon = ("Order Lifting or Reopening in the Next Week", (soup.find("div", class_="g-list-container g-cat-soon")).find_all("div", class_="g-state g-cat-soon "))
            except:
                soon = ("",[])
        try:
            shutdown = ("Shut down or restricted", (soup.find("div", class_="g-list-container g-cat-shutdown-restricted")).find_all("div", class_="g-state g-cat-shutdown-restricted"))
        except:
            try:
                shutdown = ("Shut down or restricted", (soup.find("div", class_="g-list-container g-cat-shutdown-restricted")).find_all("div", class_="g-state g-cat-shutdown-restricted "))
            except:
                shutdown = ("",[])
        try:
            regional = ("Regional Reopening", (soup.find("div", class_="g-list-container g-cat-regional")).find_all("div", class_="g-state g-cat-regional"))
        except:
            try:
                regional = ("Regional Reopening", (soup.find("div", class_="g-list-container g-cat-regional")).find_all("div", class_="g-state g-cat-regional "))
            except:
                regional = ("",[])
        
        if not reopened[1] and not forward[1] and not pausing[1] and not reversing[1] and not reopening[1] and not soon[1] and not shutdown[1] and not regional[1]:
            print("No data collected for " + last_updated)
        all_status = [reopened, forward, pausing, reversing, reopening, soon, shutdown, regional]
        # Iterating through all status
        for status in all_status:
            status_val, div = status
            # Iterate through states in status
            for state in div:
                st_ab = state["data-state"]
                try:
                    open_ests = (state.find("div", class_="g-details-wrap g-details")).find_all("div", class_="g-cat-details-wrap")
                except:
                    try:
                        open_ests = (state.find("div", class_="g-details-wrap g-details")).find_all("div", class_="g-cat-name-text-wrap")
                    except:
                        open_ests = []
                try:
                    closed_ests = (state.find("div", class_="g-details-wrap g-details_closed")).find_all("div", class_="g-cat-details-wrap")
                except:
                    try:
                        closed_ests = (state.find("div", class_="g-details-wrap g-details_closed")).find_all("div", class_="g-cat-name-text-wrap")
                    except:
                        closed_ests = []
                try:
                    reopening_ests = (state.find("div", class_="g-details-wrap")).find_all("div", class_="g-cat-details-wrap")
                except:
                    try:
                        reopening_ests = (state.find("div", class_="g-details-wrap-outer")).find_all("div", class_="g-cat-name-text-wrap")
                    except:
                        reopening_ests = []
                try:
                    soon_ests =  (state.find("div", class_="g-details-wrap g-details_soon")).find_all("div", class_="g-cat-details-wrap")
                except:
                    try:
                        soon_ests =  (state.find("div", class_="g-details-wrap g-details_soon")).find_all("div", class_="g-cat-name-text-wrap")
                    except:
                        soon_ests = []
                if not open_ests and not closed_ests and not reopening_ests and not soon_ests:
                    print("No establishment data collected for " + date + ": " + st_ab)
                    continue
                # Get open ests
                for est in open_ests:
                    row = {
                        "Report Date": last_updated,
                        "State": st_ab,
                        "State Status": status_val,
                        "Establishment Category": est.find("div", class_="g-cat-name").text,
                        "Establishment Status": "Open",
                        "Establishment Details": est.find("div", class_="g-cat-text").text
                    }
                    rows.append(row)
                # Get closed ests
                for est in closed_ests:
                    row = {
                        "Report Date": last_updated,
                        "State": st_ab,
                        "State Status": status_val,
                        "Establishment Category": est.find("div", class_="g-cat-name").text,
                        "Establishment Status": "Closed",
                        "Establishment Details": est.find("div", class_="g-cat-text").text
                    }
                    rows.append(row)
                # Get reopening ests
                for est in reopening_ests:
                    row = {
                        "Report Date": last_updated,
                        "State": st_ab,
                        "State Status": status_val,
                        "Establishment Category": est.find("div", class_="g-cat-name").text,
                        "Establishment Status": "Reopened",
                        "Establishment Details": est.find("div", class_="g-cat-text").text
                    }
                    rows.append(row)
                # Get soon ests
                for est in soon_ests:
                    row = {
                        "Report Date": last_updated,
                        "State": st_ab,
                        "State Status": status_val,
                        "Establishment Category": est.find("div", class_="g-cat-name").text,
                        "Establishment Status": "Reopening soon",
                        "Establishment Details": est.find("div", class_="g-cat-text").text
                    }
                    rows.append(row)
        # Output 
        for row in rows:
            fields = sorted([x for x in row])
            exists = os.path.exists(data)
            with open(data, "a") as fp:
                writer = csv.writer(fp)
                if not exists:
                    writer.writerow(fields)
                writer.writerow([row[x] for x in fields])


def get_hist():
    # Getting all dates
    data = "nytimes.csv"
    base_dt = datetime.now() - timedelta(days=1)
    date_list = [base_dt - timedelta(days=x) for x in range(83)]
    date_list = [x.strftime("%Y%m%d") for x in date_list]
    rows = []
    collected = set()
    # Going through all dates
    for date in date_list:
        url = ("https://web.archive.org/web/%s/https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html" % date)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = Request(url=url, headers=headers) 
        html = urlopen(req).read() 
        soup = BeautifulSoup(html, "html.parser")
        # Get last updated
        last_updated = (soup.find("time", class_="css-wcxsge").text).replace("Updated", "").strip()
        if last_updated in collected:
            continue
        else:
            collected.add(last_updated)
            print(last_updated)
        # Getting each status div
        try:
            reopened = ("Reopened", (soup.find("div", class_="g-list-container g-cat-reopened")).find_all("div", class_="g-state g-cat-reopened"))
        except:
            try:
                reopened = ("Reopened", (soup.find("div", class_="g-list-container g-cat-reopened")).find_all("div", class_="g-state g-cat-reopened "))
            except:
                reopened = ("",[])
        try:
            forward = ("Forward", (soup.find("div", class_="g-list-container g-cat-forward")).find_all("div", class_="g-state g-cat-forward"))
        except:
            try:
                forward = ("Forward", (soup.find("div", class_="g-list-container g-cat-forward")).find_all("div", class_="g-state g-cat-forward "))
            except:
                forward = ("",[])
        try:
            pausing = ("Pausing", (soup.find("div", class_="g-list-container g-cat-pausing")).find_all("div", class_="g-state g-cat-pausing"))
        except:
            try:
                pausing = ("Pausing", (soup.find("div", class_="g-list-container g-cat-pausing")).find_all("div", class_="g-state g-cat-pausing "))
            except:
                pausing = ("",[])
        try:
            reversing = ("Reversing", (soup.find("div", class_="g-list-container g-cat-reversing")).find_all("div", class_="g-state g-cat-reversing"))
        except:
            try:
                reversing = ("Reversing", (soup.find("div", class_="g-list-container g-cat-reversing")).find_all("div", class_="g-state g-cat-reversing "))
            except:
                reversing = ("",[])
        try:
            reopening = ("Reopening", (soup.find("div", class_="g-list-container g-cat-reopening")).find_all("div", class_="g-state g-cat-reopening"))
        except:
            try:
                reopening = ("Reopening", (soup.find("div", class_="g-list-container g-cat-reopening")).find_all("div", class_="g-state g-cat-reopening "))
            except:
                reopening = ("",[])
        try:
            soon = ("Order Lifting or Reopening in the Next Week", (soup.find("div", class_="g-list-container g-cat-soon")).find_all("div", class_="g-state g-cat-soon"))
        except:
            try:
                soon = ("Order Lifting or Reopening in the Next Week", (soup.find("div", class_="g-list-container g-cat-soon")).find_all("div", class_="g-state g-cat-soon "))
            except:
                soon = ("",[])
        try:
            shutdown = ("Shut down or restricted", (soup.find("div", class_="g-list-container g-cat-shutdown-restricted")).find_all("div", class_="g-state g-cat-shutdown-restricted"))
        except:
            try:
                shutdown = ("Shut down or restricted", (soup.find("div", class_="g-list-container g-cat-shutdown-restricted")).find_all("div", class_="g-state g-cat-shutdown-restricted "))
            except:
                shutdown = ("",[])
        try:
            regional = ("Regional Reopening", (soup.find("div", class_="g-list-container g-cat-regional")).find_all("div", class_="g-state g-cat-regional"))
        except:
            try:
                regional = ("Regional Reopening", (soup.find("div", class_="g-list-container g-cat-regional")).find_all("div", class_="g-state g-cat-regional "))
            except:
                regional = ("",[])
        
        if not reopened[1] and not forward[1] and not pausing[1] and not reversing[1] and not reopening[1] and not soon[1] and not shutdown[1] and not regional[1]:
            print("No data collected for " + date)
            continue
        all_status = [reopened, forward, pausing, reversing, reopening, soon, shutdown, regional]
        # Iterating through all status
        for status in all_status:
            status_val, div = status
            # Iterate through states in status
            for state in div:
                st_ab = state["data-state"]
                try:
                    open_ests = (state.find("div", class_="g-details-wrap g-details")).find_all("div", class_="g-cat-details-wrap")
                except:
                    try:
                        open_ests = (state.find("div", class_="g-details-wrap g-details")).find_all("div", class_="g-cat-name-text-wrap")
                    except:
                        open_ests = []
                try:
                    closed_ests = (state.find("div", class_="g-details-wrap g-details_closed")).find_all("div", class_="g-cat-details-wrap")
                except:
                    try:
                        closed_ests = (state.find("div", class_="g-details-wrap g-details_closed")).find_all("div", class_="g-cat-name-text-wrap")
                    except:
                        closed_ests = []
                try:
                    reopening_ests = (state.find("div", class_="g-details-wrap")).find_all("div", class_="g-cat-details-wrap")
                except:
                    try:
                        reopening_ests = (state.find("div", class_="g-details-wrap-outer")).find_all("div", class_="g-cat-name-text-wrap")
                    except:
                        reopening_ests = []
                try:
                    soon_ests =  (state.find("div", class_="g-details-wrap g-details_soon")).find_all("div", class_="g-cat-details-wrap")
                except:
                    try:
                        soon_ests =  (state.find("div", class_="g-details-wrap g-details_soon")).find_all("div", class_="g-cat-name-text-wrap")
                    except:
                        soon_ests = []
                if not open_ests and not closed_ests and not reopening_ests and not soon_ests:
                    print("No establishment data collected for " + date + ": " + st_ab)
                    continue
                # Get open ests
                for est in open_ests:
                    row = {
                        "Report Date": last_updated,
                        "State": st_ab,
                        "State Status": status_val,
                        "Establishment Category": est.find("div", class_="g-cat-name").text,
                        "Establishment Status": "Open",
                        "Establishment Details": est.find("div", class_="g-cat-text").text
                    }
                    rows.append(row)
                # Get closed ests
                for est in closed_ests:
                    row = {
                        "Report Date": last_updated,
                        "State": st_ab,
                        "State Status": status_val,
                        "Establishment Category": est.find("div", class_="g-cat-name").text,
                        "Establishment Status": "Closed",
                        "Establishment Details": est.find("div", class_="g-cat-text").text
                    }
                    rows.append(row)
                # Get reopening ests
                for est in reopening_ests:
                    row = {
                        "Report Date": last_updated,
                        "State": st_ab,
                        "State Status": status_val,
                        "Establishment Category": est.find("div", class_="g-cat-name").text,
                        "Establishment Status": "Reopened",
                        "Establishment Details": est.find("div", class_="g-cat-text").text
                    }
                    rows.append(row)
                # Get soon ests
                for est in soon_ests:
                    row = {
                        "Report Date": last_updated,
                        "State": st_ab,
                        "State Status": status_val,
                        "Establishment Category": est.find("div", class_="g-cat-name").text,
                        "Establishment Status": "Reopening soon",
                        "Establishment Details": est.find("div", class_="g-cat-text").text
                    }
                    rows.append(row)
    # Output 
    for row in rows:
        fields = sorted([x for x in row])
        exists = os.path.exists(data)
        with open(data, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([row[x] for x in fields])

def get_masks():
    url = "https://www.cnn.com/2020/06/19/us/states-face-mask-coronavirus-trnd/index.html"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url=url, headers=headers) 
    html = urlopen(req).read() 
    soup = BeautifulSoup(html, "html.parser")
    states = soup.find_all("h3")
    dates = soup.find_all("strong")
    dates = [x for x in dates if x.text != " "]
    rows = []
    for state, date in zip(states, dates):
        row = {
            "State": state.text,
            "Requiring Masks As Of": ((date.text).replace("As of ", "")).replace(":", "")
        }
        rows.append(row)
    data = "cnn_masks.csv"
    # Output 
    for row in rows:
        fields = sorted([x for x in row])
        exists = os.path.exists(data)
        with open(data, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(fields)
            writer.writerow([row[x] for x in fields])
# get_masks()
# exit()
scrape()
# # Get historical
# get_hist()
# exit()


# writer = csv.writer(sys.stdout)
# writer.writerow(["state", "stateAbbrev", "place", "wholeState", "pop",
#                  "order", "orderEff", "orderLink", "newsLink", "pullTime"])

# html = urlopen("https://www.nytimes.com/interactive/2020/us/coronavirus-stay-at-home-order.html").read()
# soup = BeautifulSoup(html, "html.parser")
# for x in soup.find_all("div", class_="state-wrap"):
#     stateAbbrev = x["data-state"].strip()
#     state = x.h3.find(text=True).strip()
#     if "statewide" in x["class"]:
#         place, pop, order, dt, orderLink, newsLink = getPlace(x.div)
#         pop = getPop(x.h3.span.text)
#         writer.writerow([state, stateAbbrev, state, 1, pop,
#                          order, dt, orderLink, newsLink, now])
#     else:
#         for place in x.findChildren("div", class_="place-wrap"):
#             place, pop, order, dt, orderLink, newsLink = getPlace(place)
#             writer.writerow([state, stateAbbrev, place, 0, pop,
#                              order, dt, orderLink, newsLink, now])
