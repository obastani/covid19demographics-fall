import re
import pandas as pd
import boto3
import os
import dask
import dask.dataframe as dd
import glob
from datetime import datetime

def core_places():
   # Get core places 
    core_path = "../../safegraph/raw/core_places/"
    list_df = []
    for file in os.listdir(core_path):
        if ".csv.gz" in file:
            core_df = pd.read_csv(core_path + file,
                                  compression='gzip',
                                  usecols=["safegraph_place_id",
                                           "location_name",
                                           "top_category",
                                           "naics_code"])
            core_df = core_df[core_df["naics_code"].notna()]
            list_df.append(core_df)
    monthly_df_core_places = pd.concat(list_df)
    airport_naics = [488111, 488119]    
    airports_df = monthly_df_core_places.loc[monthly_df_core_places["naics_code"].isin(airport_naics)]
    airports_safegraphid = []
    for index, value in airports_df["safegraph_place_id"].iteritems():
        airports_safegraphid.append(value)
    print(len(airports_safegraphid))
    return airports_safegraphid

def get_current_month(month, airports_safegraphid):
    # Get patterns
    path = "../../safegraph/raw/monthly_patterns/" + month
    list_pat = []
    for file in os.listdir(path):
        if ".csv.gz" in file:
            monthly_df_patterns = pd.read_csv(path + "/" + file,
                                              compression="gzip",
                                              usecols=["safegraph_place_id",
                                                      "location_name",
                                                      "date_range_start",
                                                      "date_range_end",
                                                      "visitor_home_cbgs",
                                                      "visitor_daytime_cbgs",
                                                      "visitor_work_cbgs"])
            airport_patterns = monthly_df_patterns.loc[monthly_df_patterns["safegraph_place_id"].isin(airports_safegraphid)]
            list_pat.append(airport_patterns)
    
    airport_patterns = pd.concat(list_pat)
    export_path = "../safegraph/data/monthly_patterns/data_" + month.replace("/","_") + ".csv.gz"
    airport_patterns.to_csv(export_path, compression="gzip")
    print(month, airport_patterns.shape)

def get_weekly(airports_safegraphid):
    # Path
    path = "../../safegraph/raw/weekly_patterns/"
    for file in os.listdir(path):
        if ".csv.gz" in file:
            weekly_df_patterns = pd.read_csv(path + file,
                                              compression="gzip",
                                              usecols=["safegraph_place_id",
                                                      "location_name",
                                                      "date_range_start",
                                                      "date_range_end",
                                                      "visitor_home_cbgs"])
            airport_patterns = weekly_df_patterns.loc[weekly_df_patterns["safegraph_place_id"].isin(airports_safegraphid)]
            export_path = "../safegraph/data/weekly_patterns/airport_data_" + file
            airport_patterns.to_csv(export_path, compression="gzip")
            print(file, airport_patterns.shape)
def get_social_distancing():
    path = "../../safegraph/raw/social_distancing/2020/"
    export_path = "../../safegraph/data/social_distancing/"
    for month in os.listdir(path):
        if int(month) < 5:
            continue
        print("Started: Month " + str(month))
        monthly_sd = []
        for day in os.listdir(path + month + "/"):
            # if int(month) == 5 and int(day) < 13:
            #     continue
            for file in os.listdir(path + month + "/" + day + "/"):
                if ".csv.gz" in file:
                    daily_sd = pd.read_csv(path + month + "/" + day + "/" + file,
                                           compression="gzip",
                                           usecols=["origin_census_block_group",
                                                    "date_range_start",
                                                    "date_range_end",
                                                    "device_count",
                                                    "completely_home_device_count",
                                                    "median_percentage_time_home",
                                                    "part_time_work_behavior_devices",
                                                    "full_time_work_behavior_devices",
                                                    "delivery_behavior_devices",
                                                    "candidate_device_count",
                                                    # "mean_home_dwell_time",
                                                    # "mean_non_home_dwell_time",
                                                    # "mean_distance_traveled_from_home",
                                                    # "bucketed_away_from_home_time",
                                                    # "bucketed_distance_traveled",
                                                    # "bucketed_home_dwell_time",
                                                    # "bucketed_percentage_time_home"
                                           ]
                    )
                    monthly_sd.append(daily_sd)
        monthly_merged = pd.concat(monthly_sd)
        monthly_merged.to_csv(export_path + "2020_" + month + "_basic_social_distancing.csv.gz", compression="gzip")
        print("Exported")

def run_SafeGraph(args):
    # safegraph_session = boto3.Session(profile_name='safegraph')
    # safegraph_credentials = safegraph_session.get_credentials().get_frozen_credentials()
    # safegraph_storage_options = {'key': safegraph_credentials.access_key,
    #                              'secret': safegraph_credentials.secret_key}
    # airports_safegraphid = core_places()
    # months = []
    # for i in range(12):
    #     if i < 9:
    #         months.append("2019/0" + str(i+1))
    #     else:
    #         months.append("2019/" + str(i+1))

    # for month in months:
    #     get_current_month(month, airports_safegraphid)
    
    #get_weekly(airports_safegraphid)
    get_social_distancing()

if __name__ == '__main__':
    run_SafeGraph({})