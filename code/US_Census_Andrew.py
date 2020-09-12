import os
import csv
import pandas as pd
from datetime import datetime

def run_Census(args):
    # Get tables and keys
    age_dist = pd.read_csv("../US_Census/raw/data/cbg_b01.csv")
    cbg_fips_codes = pd.read_csv("../US_Census/raw/metadata/cbg_fips_codes.csv")
    cbg_key = pd.read_csv("../US_Census/raw/metadata/cbg_field_descriptions.csv")
    
    # Process raw
    drop_cols = []
    for col in age_dist.columns:
        if ("1001" not in col) and ("census_block_group" != col):
            drop_cols.append(col)
    age_dist = age_dist.drop(columns=drop_cols)

    # Splitting Error from Estimate
    error_data = age_dist
    error_cols =[]
    estimate_cols = []
    for col in age_dist.columns:
        if "census_block_group" != col:
            if "m" in col:
                error_cols.append(col)
            else:
                estimate_cols.append(col)
    error_data = error_data.drop(columns=estimate_cols)
    age_dist = age_dist.drop(columns=error_cols)

    # Renaming Columns
    age_dist = age_dist.rename(columns=dict(zip(cbg_key["table_id"],cbg_key["field_full_name"] )))
    error_data = error_data.rename(columns=dict(zip(cbg_key["table_id"],cbg_key["field_full_name"] )))

    # Assigning State to age_dist
    for index, row in age_dist.iterrows():
        state_code = 0
        if len(str(row["census_block_group"])) == 11:
            state_code = int(str(row["census_block_group"])[0])
        elif len(str(row["census_block_group"])) == 12:
            state_code = int(str(row["census_block_group"])[0:2])
        else:
            raise Exception("FIPS unexpected size")
        age_dist.at[index, "census_block_group"] = state_code
    
    # Aggregating data by state
    state_codes = age_dist["census_block_group"].drop_duplicates().tolist()
    agg_data = []
    for code in state_codes:
        state_data = {}
        for col in age_dist.columns:
            if col == "census_block_group":
                continue
            else:
                sum_val = age_dist.loc[age_dist["census_block_group"] == code, col].sum()
                new_col = (col.replace("SEX BY AGE: ", "")).replace(": Total population -- (Estimate)", "")
                state_data[new_col] = sum_val
        state_data["state_fips"] = code
        agg_data.append(state_data)

    agg_df = pd.DataFrame(agg_data)
    
    # Merge with FIPS state_code so we know what state we are talking about
    cbg_fips_codes = cbg_fips_codes.drop(columns=["county", "class_code", "county_fips"])
    cbg_fips_codes.drop_duplicates(subset="state_fips", keep="first", inplace=True)
    output = agg_df.merge(cbg_fips_codes, on="state_fips")
    
    # Export file
    output.to_csv("../US_Census/data/data.csv", index=False)




if __name__ == "__main__":
    run_Census({})