from pathlib import Path
import os, sys
import requests as requests
rq = requests
import base64
import hashlib
import datetime
from bs4 import BeautifulSoup
import dateutil.parser as dparser
import json
import pandas as pd
import numpy as np
import re
import hjson
#import html5lib
import io
import time


project_root = Path(__file__).resolve().parent.parent.parent

def cache_hash(string):
    H = hashlib.sha1(string.encode())
    output = base64.urlsafe_b64encode(H.digest()[:10])
    output = ''.join([c for c in output.decode() if c.isalnum()])
    return(output)


def cache_filename(url, date=False, state=False, extension=''):
    assert date
    assert state

    url = url.split('//')[1]
    url_alnum = "".join(char for char in url if char.isalnum())
    url_stub = url_alnum[0:24]
    url_hash = cache_hash(url)
    if extension!='' and extension[0]!='.':
        extension = f'.{extension}'
    filename = f'{state}_{date}_{url_stub}_{url_hash}{extension}'
    return(filename)

def get_timeseries_files(url, end_date=False, state=False):
    folderpath = Path(project_root, state, 'raw')
    all_files = os.listdir(folderpath)
    url_hash = cache_hash(url.split('//')[1])
    matching_files = [f for f in all_files if f.endswith(url_hash)]


def fetch_(url, 
    date=False, state=False, extension='',
    force=False, verbose=False, time_travel=False,
    headers={}, save=True, method='GET', payload=None
    ):
    assert date 
    assert state

    filename = cache_filename(url, date=date, state=state, extension=extension)
    folderpath = Path(project_root, state, 'raw')
    filepath = Path(folderpath, filename)
    
    # First check that the folder exists. If it does
    # not already exist, create the folder.
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
        if verbose:
            print("Created folder at: \n\t{}".format(folderpath))
    
    # Check if a file at that path already exists
    if os.path.isfile(filepath) and force==False:
        # If the file already exists, simply load the
        # HTML that was already downloaded
        if extension=='':
            with open(filepath, 'r') as file:
                raw_text = file.read()
        else:
            with open(filepath, 'rb') as file:
                raw_content = file.read()
            raw_content = io.BytesIO(raw_content)
            return(raw_content)


        if verbose:
            print('Retrieved data from local file: \n\t{}'.format(filepath))
            
    else:
        # If date is past, don't fetch new under current date
        if (dparser.parse(date).date() < datetime.date.today()):
            if time_travel==False:
                print('Requested date/file not cached (cannot travel back in time!)')
                print(filepath)
                return(False)

            elif time_travel=='wayback':
                wayback_query_url = f'https://archive.org/wayback/available?url={url}&timestamp={date.replace("-","")}20'
                wayback = requests.get(wayback_query_url)
                wayback_response = wayback.json()
                if len(wayback_response["archived_snapshots"].items()) == 0:
                    print('No snapshots on Wayback Machine.')
                    return(False)

                wayback_ts = wayback_response["archived_snapshots"]["closest"]["timestamp"]
                wayback_dt = dparser.parse(wayback_ts)
                target_dt = dparser.parse(date + ' 20:00')
                wayback_dt

                hours_ahead = (wayback_dt-target_dt).seconds/3600
                if (wayback_dt-target_dt).days<0:
                    hours_ahead = 0
                hours_behind = (target_dt-wayback_dt).seconds/3600
                if (target_dt-wayback_dt).days<0:
                    hours_behind = 0

                if hours_ahead>8 or hours_behind>8:
                    #print(hours_ahead,hours_behind)
                    print(f"Wayback Machine snapshot not available for date; closest snapshot timestamp: {wayback_dt}")
                    return(False)

                wayback_url = wayback_response["archived_snapshots"]["closest"]["url"]
                wayback_url_splits = wayback_url.split('/')
                wayback_url_splits[4] = wayback_url_splits[4] + 'id_'
                url = '/'.join(wayback_url_splits)
                print(f"Using Wayback snapshot at timestamp: {wayback_dt}")
                print(url)

        # If a file with this filename does NOT already
        # exist, fetch the URL from the web

        # add spoofed user agent header
        if 'User-Agent' not in headers:
            spoofed_ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'
            headers = {
                **headers,
                'User-Agent': spoofed_ua
            }
        if method=='GET':
            try:
                response = requests.get(url, headers=headers)
            except requests.exceptions.SSLError:
                response = requests.get(url, headers=headers, verify=False)
        elif method=='POST':
            response = requests.post(url, headers=headers, data=payload)

        if response.status_code!=200:
            print(f'Error code: {response.status_code}')
            print(f'Error response: {response.text[0:1000]}')
            return(False)

        
        if url.endswith('.xlsx') or extension=='xlsx':
            if save:
                with open(filepath, 'wb+') as file:
                    file.write(response.content)
            print("Note: 'fetch' returning .xlsx bytes content.")
            raw_content = io.BytesIO(response.content)
            return(raw_content)

        else:
            raw_text = response.text
            if save:
                try:
                    with open(filepath, 'w+') as file:
                        file.write(raw_text)
                except UnicodeEncodeError:
                    with open(filepath, 'wb+') as file:
                        file.write(raw_text.encode('utf8'))
            
        if verbose:
            msg = 'Retrieved HTML from web'
            if save:
                msg += ' and saved contents to local file: \n\t{}'.format(filepath)
            print(msg)
    
    return(raw_text)

def get_pull_time(existing_df, row_date):

    # If pullTime can be read from previous data, use that.
    if existing_df.shape[0]>0 and\
        'date' in existing_df.columns and\
        'pullTime' in existing_df.columns and\
        row_date in existing_df.date.tolist():

        pullTime = str(existing_df.loc[existing_df.date==row_date, 'pullTime'].values[0])
        if '\\n' in pullTime:
            pullTime = pullTime.split('\\n')[0].split('    ')[-1]

        if '\nName' in pullTime:
            pullTime = pullTime.split('\nName')[0].split('    ')[-1]

    # If row_date is in past, just use date
    elif row_date < datetime.datetime.now().strftime('%Y-%m-%d'):
        pullTime = f'{dparser.parse(row_date)}'

    # If row_date is today, use timestamp
    else:
        pullTime = f'{datetime.datetime.now()}'

    return(pullTime)