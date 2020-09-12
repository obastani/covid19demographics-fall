from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys
from urllib.request import urlopen
import os
import requests
from io import BytesIO
from io import StringIO
from PIL import Image
import pytesseract

def grabImg(url, fname):
    # Grab png
    r = requests.get(url)
    if not r.ok:
        raise Exception("Error accessing " + url)
    with open(fname, 'wb') as f:
        f.write(r.content)
    return Image.open(BytesIO(r.content))

def grabDataPixels(img, prefix, out):
    cols, rows = img.size
    pix = img.load()
    batches = []
    currbatch = []
    for c in range (cols):
        colmatch = False
        for r in range(rows):
            if (pix[c,r][0] <= 10 and pix[c,r][1] <= 40 and pix[c,r][2] <= 130):
                colmatch = True
                currbatch.append((r, c))
        if not colmatch and len(currbatch) > 0:
            batches.append((min([x[0] for x in currbatch]), max([x[0] for x in currbatch]), min([x[1] for x in currbatch]), max([x[1] for x in currbatch])))
            currbatch = []
    if len(currbatch) > 0:
        batches.append((min([x[0] for x in currbatch]), max([x[0] for x in currbatch]), min([x[1] for x in currbatch]), max([x[1] for x in currbatch])))

def grabDataOCR(img, prefix, out):
    str_image = pytesseract.image_to_string(img)
    f = open(prefix + "_ocr.txt", "w")
    f.write(str_image)
    f.close
    # print(str_image)

def run_NC(args):
    # Parameters
    raw_name = '../NC/raw'
    data_name = '../NC/data/data.csv'
    now = str(datetime.now())

    # Open file
    exists = os.path.exists(data_name)
    f = open(data_name, 'a')
    writer = csv.writer(f)
    if not exists:
        writer.writerow(["Age [0-17]", "Age [18-24]", "Age [25-49]", "Age [50-64]", "Age [65+]",
                         "Female", "Male", "Unknown", "ICU Beds Used", "ICU Beds Empty", "Inpatient Beds Used", "Inpatient Beds Empty", "pullTime"])

    # Scrape data
    now = datetime.now()
    html = urlopen("https://www.ncdhhs.gov/covid-19-case-count-nc").read()
    soup = BeautifulSoup(html, "html.parser")
    g = open('{}/{}.html'.format(raw_name, now), 'w')
    g.write(str(soup))
    g.close()

    # Get relevant images
    baseurl = "https://files.nc.gov/ncdhhs/"
    filenames = ["CasebyAge.jpg",
                 "DeathbyAge.jpg",
                 "CasebyGender.jpg",
                 "DeathbyGender.jpg",
                 "InpatientHospitalBed.jpg",
                 "Ventilators.jpg", 
                 "PPE.jpg"
                ]
    imagesList = []
    for file in filenames:
        name_nosuffix = re.sub("\.jpg$","", file)
        imageObj = grabImg(baseurl + file, "%s/" % raw_name + name_nosuffix + "_%s.png" % now)
        imagesList.append({"name": name_nosuffix, "object": imageObj})

    # Get data 
    out = {}
    for image in imagesList:
        #if image["name"] == "CasebyAge":
        grabDataOCR(image["object"], image["name"], out)
        #else:
            #break
        

    # Get age distribution
    # age1 = int(list(list(soup(text='0-17')[0].parent.parent.children)[2].children)[0][:-1])/100
    # age2 = int(list(list(soup(text='18-24')[0].parent.parent.children)[2].children)[0][:-1])/100
    # age3 = int(list(list(soup(text='25-49')[0].parent.parent.children)[2].children)[0][:-1])/100
    # age4 = int(list(list(soup(text='50-64')[0].parent.parent.children)[2].children)[0][:-1])/100
    # age5 = int(list(list(soup(text='65+')[0].parent.parent.children)[2].children)[0][:-1])/100

    # # Get gender distribution
    # female = int(list(list(soup(text='Female')[0].parent.parent.children)[2].children)[0][:-1])/100
    # male = int(list(list(soup(text='Male')[0].parent.parent.children)[2].children)[0][:-1])/100
    # unknown = int(list(list(soup(text='Unknown')[0].parent.parent.children)[2].children)[0][:-1])/100

    # # Get ICU bed usage
    # icu = int(list(list(soup(text='Intensive Care Unit (ICU) Beds')[0].parent.parent.children)[2].children)[0].replace(',', ''))
    # icu_empty = int(list(list(soup(text='Intensive Care Unit (ICU) Beds')[0].parent.parent.children)[4].children)[0].replace(',', ''))
    # beds = int(list(list(soup(text='Inpatient Hospital Beds')[0].parent.parent.children)[2].children)[0].replace(',', ''))
    # beds_empty = int(list(list(soup(text='Inpatient Hospital Beds')[0].parent.parent.children)[4].children)[0].replace(',', ''))

    # # Write row
    # writer.writerow([age1, age2, age3, age4, age5, female, male, unknown, icu, icu_empty, beds, beds_empty, now])

    # # Close file
    # f.close()

if __name__ == '__main__':
    run_NC({})
