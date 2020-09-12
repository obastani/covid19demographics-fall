#!/bin/bash
# Activate Env
cd code
source env/bin/activate
# Run nytimes
cd ../nytimes
python3 nytimes_scrape.py
# Run main on Alex
cd ../code_alex
python3 main.py
# Run main on Code
cd ../code
python3 main.py
# Run did_scrape
python3 did_scrape.py