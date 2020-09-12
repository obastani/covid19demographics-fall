import os
import pandas as pd
import csv
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import compress_json

def export_key(out):
    """Export Generated Key Template"""
    data_name = "Master_Key/master_key.csv"
    exists = os.path.exists(data_name)
    if exists:
        for i in range(100):
            if not os.path.exists("Master_Key/master_key_v%s.csv" % (i+ 1)):
                os.rename(data_name, "Master_Key/master_key_v%s.csv" % (i+ 1))
                break
    for row in out:
        out_fields = [x for x in row]
        exists = os.path.exists(data_name)
        with open(data_name, "a") as fp:
            writer = csv.writer(fp)
            if not exists:
                writer.writerow(out_fields)
            writer.writerow([row[x] for x in out_fields])

def format_data(folders):
    """Format data to be added to template"""
    out = []
    for key in folders:
        df = pd.read_csv(key)
        for col in folders[key]["cols"]:
            # print(df[col].dtype)
            row = {
                "File": key,
                "State": folders[key]["state"],
                "Column Name": col,
                "Category": "",
                "New Key": "",
                "Data Type": (df[col]).dtype
            }
            out.append(row)
    return out

def iterate_dir():
    """Iterate through directory to get all column names of all files"""
    unwanted = ["SouthKoreaCensus", "US_Census", "unacast", "nytimes"]
    directory = "../../../covid19-data"
    folders = {}
    for folder in os.listdir(directory):
        if folder in unwanted:
            continue
        path = directory + "/" + folder + "/data/"
        if os.path.exists(path):
            for filename in os.listdir(path):
                if filename.endswith(".csv"):
                    # print(folder, filename)
                    try:
                        df = pd.read_csv(path + filename)
                    except:
                        print(folder, filename)
                        raise 
                    folders[path + filename] = {
                        "state": folder,
                        "cols": df.columns
                    }
    return folders

def fix_percentages(current_df, current_file):
    """Fix percentages format from decimal to full number and check to see % values make sense"""
    sum_pct = 0
    pct_cols = []
    # Iterate through all columns
    for col in current_df.columns:
        # If a percentage column
        if type(col) != str:
            print("Irregular column name " + str(col) + " in " + current_file)
            continue
        if "%" in col:
            pct_cols.append(col)
            # If string, convert to numeric, ignoring errors
            if current_df[col].dtypes == "object":
                current_df[col] = pd.to_numeric(current_df[col], errors ="ignore")
            # Getting virst valid row index
            valid_index = current_df[col].first_valid_index()
            # If value still continues to be string, then strip % sign or raise exception
            if isinstance(current_df.loc[valid_index, col], str):
                if "%" in current_df.loc[valid_index, col]:
                    current_df.loc[valid_index, col] = float(current_df.loc[valid_index, col].strip("%"))
                else:
                    raise Exception(current_file, current_df.loc[valid_index, col])
            # # If value is less than 1, multiply by 100
            # if current_df.loc[valid_index, col] < 1:
            #     current_df[col] *= 100
            # # If value equals 1, check next index to see if it is less than 1, if so convert
            # elif current_df.loc[valid_index, col] == 1:
            #     if current_df.loc[valid_index + 1, col] < 1:
            #         current_df[col] *= 100
            # # If value is greater than 100, raise problem - needs to be checked
            sum_pct += current_df.loc[valid_index, col]
            if current_df.loc[valid_index, col] > 103:
                print(current_file, col, current_df.loc[valid_index, col])
    
    # Check sum_pct to see if we are dealing with decimals or not
    #print(current_file, sum_pct, len(pct_cols))
    if sum_pct < 60:
        for col in pct_cols:
            if current_df.loc[valid_index, col] <= 1:
                current_df[col] *= 100
    return current_df

def fix_na(current_df, current_file):
    """Find out which columns have NA values"""
    na_df = current_df.isna().any().to_frame()
    file_array = [current_file for i in range(len(current_df.isna().any()))]
    na_df['File'] = file_array
    return na_df

def output_na(na_list):
    curr_df = pd.concat(na_list)
    # Export to CSV
    data_name = "NAs/columns_na_list.csv"
    exists = os.path.exists(data_name)
    if exists:
        for i in range(100):
            if not os.path.exists("NAs/columns_na_list_v%s.csv" % (i+ 1)): 
                os.rename(data_name, "NAs/columns_na_list_v%s.csv" % (i+ 1))
                break
    curr_df.to_csv(data_name)

def remove_dup(current_df, current_file):
    # Drop identical rows
    current_df = current_df.drop_duplicates()
    # Don't attempt with county
    if "county" in current_file or "zip" in current_file:
        # print(current_file)
        return current_df
    for col in current_df.columns:
        try:
            if "county" in col.lower() or "zip" in col.lower() or "fips" in col.lower():
                return current_df
        except:
            print("Irregular column name [" + str(col) + "] in " + current_file)
    # Drop identical report dates
    if "Report Date" in current_df.columns:
        current_df = current_df.drop_duplicates(subset="Report Date")
        return current_df
    
    # Remove duplicates based on scrape time
    if "Scrape Time" not in current_df.columns:
        return current_df
    try:
        current_df["Scrape Time"] = pd.to_datetime(current_df["Scrape Time"])
    except:
        print("Unable to convert Scrape time to datetime in: " + current_file)
        return current_df
    current_df = current_df.sort_values(by=["Scrape Time"])
    prev_dt = None
    for index, row in current_df.iterrows():
        if prev_dt == None:
            prev_dt = row["Scrape Time"]
            continue
        diff = row["Scrape Time"] - prev_dt

        # If difference is less than 8 hours, drop row
        if diff.total_seconds() <= 8*60*60:
            current_df.drop(index, inplace = True)
        else:
            prev_dt = row["Scrape Time"]
    
    # Convert datetime back to string to be able to JSONify
    current_df["Scrape Time"] = current_df["Scrape Time"].dt.strftime("%Y-%m-%d %r")
    return current_df

def vlookup(key_df, case):
    # Helper variables
    current_file = None
    current_df = None
    current_state = None
    column_mapping = {}
    new_files = {}
    is_first = True
    na_list = []

    # Iterate through files, create copy in code that substitutes column names
    # with new keys
    for index, row in key_df.iterrows():
        # Check if file is current file - avoid reading df again
        if row['File'] != current_file:
            if not is_first:
                # Rename current columns
                current_df.rename(columns=column_mapping, inplace=True)
                # Find and remove duplicate dates
                current_df = remove_dup(current_df, current_file)
                # Fix percentage values
                current_df = fix_percentages(current_df, current_file)
                if case == "2":
                    # Find NA values
                    na_list.append(fix_na(current_df, current_file))
                # Append df to dict
                key = (current_file.replace("../../../covid19-data/" + current_state + "/data/","")).replace(".csv","")
                if current_state not in new_files.keys():
                    new_files[current_state] = [{key: current_df}]
                else:
                    new_files[current_state].append({key: current_df})
                
                # Reset Column Mapping
                column_mapping = {}
            # Getting current information and assigning to global vars
            current_state = row["State"]
            current_file = row["File"]
            current_df = pd.read_csv(current_file)
            is_first = False
        
        # Add new key and value to column_mapping
        column_mapping[row["Column Name"]] = row["New Key"]
    
    # Append last df to new_files
     # Rename current columns
    current_df.rename(columns=column_mapping, inplace=True)
    # Find and remove duplicate dates
    current_df = remove_dup(current_df, current_file)
    # Fix percentage values
    current_df = fix_percentages(current_df, current_file)
    if case == "2":
        # Find NA values
        na_list.append(fix_na(current_df, current_file))
    # Append df to dict
    key = (current_file.replace("../../../covid19-data/" + current_state + "/data/","")).replace(".csv","")
    if current_state not in new_files.keys():
        new_files[current_state] = [{key: current_df}]
    else:
        new_files[current_state].append({key: current_df})
    
    # Output NA columns to csv file
    # if case == "2":
    #     output_na(na_list)
    
    return new_files

def create_JSON(case):
    """"Create JSON with all Data"""
    # Read CSV
    key_file = "Master_Key/master_key.csv"
    key_df = pd.read_csv(key_file)
    key_df = key_df.sort_values(by=["File"])

    # Remove Unacast
    key_df = key_df[key_df["File"] != "../../../covid19-data/unacast/data/2020-04-07 22:39:47.057978.csv"]

    new_files = vlookup(key_df, case)
    
    out = {
        "USA": {},
        "Intl.": {}
    }

    intl_keys = ["Iceland", "SouthKorea", "SouthKoreaCensus"]
    
    # Add all rows to state key
    for state in new_files:
        international = False
        if state in intl_keys:
            out["Intl."][state] = []
            international = True
        else:
            out["USA"][state] = []
        for dic in new_files[state]:
            for key in dic:
                rows = dic[key].to_dict(orient="records")
                if international:
                    out["Intl."][state].extend(rows)
                else:
                    out["USA"][state].extend(rows)
    
    now = str(datetime.now())
        
    # Export JSON - works when running on Andrew's PC
    compress_json.dump(out, "../../../covid19demographics/data/data.json.gz")
    # with open("../../../covid19demographics/data/data_" + now +".json", "w") as fp:
    #     json.dump(out, fp)

def generate_graphs(case):
    # Read CSV
    key_file = "Master_Key/master_key.csv"
    key_df = pd.read_csv(key_file)
    key_df = key_df.sort_values(by=["File"])

    # Get data
    new_files = vlookup(key_df, case)

    # Make directory if it does not exist
    if not os.path.exists("Graphs"):
        os.mkdir("Graphs")

    # Create overall report
    files_error = []

    for state in new_files:
        for dic in new_files[state]:
            for key in dic:
                datafile = key
                # Getting path
                path = "Graphs/" + str(state) + "_" + datafile
                if not os.path.exists(path):
                    os.mkdir(path)

                # Get time variable
                time_priority = [
                    "Report Date",
                    "Scrape Time",
                    "Updated Date",
                    "Edit Date",
                    "Report Time",
                    "Entry Creation Date",
                    "Report Date Gender",
                    "Quarantine Report Date",
                    "Test Date",
                    "Last Day Test Date",
                ]
                # Determining time variable
                time_var = ""
                for time in time_priority:
                    if time in dic[key].columns:
                        time_var = time
                        break
                # Create report string
                report = ""

                if time_var == "":
                    Exception("No time variable for " + state + " in " + datafile)
                    report += "No time variable for " + state + " in " + datafile + "\n"
                    files_error.append(str(state) + "_" + datafile)
                    continue

                # Fix percentages
                current_df = fix_percentages(dic[key], path)

                # Getting NaN values:
                na_list = current_df.isna().any()
                na_cols = []
                for index, val in na_list.items():
                    if val:
                        na_cols.append(index)
                        report += (index + " contains NaN values\n")
                        files_error.append(str(state) + "_" + datafile)
                
                # Graphing every column
                for col in current_df:
                    if col not in time_priority:
                        name = col.replace("/", "_")
                        try:
                            # Check if column is numeric
                            if current_df[col].dtypes == "object":
                                report += (col + " in " + path + " is not numeric\n")
                                files_error.append(str(state) + "_" + datafile)
                            elif current_df[col].isnull().all():
                                report += ("Entire " + col + " is NaN\n")
                                files_error.append(str(state) + "_" + datafile)
                            else:
                                # Graph line
                                line = current_df.plot(x = time_var, y = col, kind = "line", rot=45, figsize = (25,15))
                                line_fig = line.get_figure()
                                line_fig.savefig(path + "/" + name + "_line.png")
                                plt.close()
                                # Graph box
                                box = current_df.boxplot(column=col)
                                box_fig = box.get_figure()
                                box_fig.savefig(path + "/" + name + "_box.png")
                                plt.close()

                                # Check for stale data and outliers
                                std = current_df[col].std(skipna=True)
                                mean = current_df[col].mean(skipna=True)
                                upper = mean + std * 3
                                lower = mean - std * 3

                                count = 1
                                prev_val = ""
                                start_time = ""
                                
                                for index, val in current_df[col].items():
                                    if val > upper or val < lower:
                                        report += (col + ": " + str(val) + " at time " + str(current_df.loc[index, time_var]) + " is an outlier in " + datafile + "\n")
                                        files_error.append(str(state) + "_" + datafile)
                                    if str(val) == prev_val:
                                        count += 1
                                    else:
                                        if count > 3:
                                            report += ("Repetitive values of " + str(val) + " in " + col + "starting at " + str(start_time) + " and ending at " + str(current_df.loc[index, time_var]) + "\n")
                                            files_error.append(str(state) + "_" + datafile)
                                        count = 1
                                        prev_val = val
                                        start_time = str(current_df.loc[index, time_var])
                        except Exception as e:
                            report += ("Unable to graph " + col + " in " + datafile + " for " + state + "\n")
                            files_error.append(str(state) + "_" + datafile)
                            print(state, datafile, col, e)

                with open(path + "/report_" + datafile + ".txt", "w") as text_file:
                    text_file.write(report)
                report = ""       
    
    uniq_error_files = []
    [uniq_error_files.append(x) for x in files_error if x not in uniq_error_files]

    rep_str = ""

    for file in uniq_error_files:
        rep_str += (str(file) + "\n")
    
    with open("Graphs/overall_report.txt", "w") as fp:
        fp.write(rep_str)


def make_key(args):
    while True:
        option = input("What do you wish to do?\n1) Create new key\n2) Create/Update JSON\n3) Generate SPC Graphs\n")
        option = option.strip()
        if option == "1":
            # Create new master_key template
            folders = iterate_dir()
            out = format_data(folders)
            export_key(out)
            break
        elif option == "2":
            # Create JSON
            create_JSON(option)
            break
        elif option == "3":
            generate_graphs(option)
            break
        else:
            print("Enter a valid input\n")
        
        
    

if __name__ == '__main__':
    make_key({})