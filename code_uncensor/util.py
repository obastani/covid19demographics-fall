import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt

# Which row in the South Korea dataframe to use.
_SK_IND = 20

# Maximum age
MAX_AGE = 89

# Path to South Korea data.
_SK_PATH = '../SouthKorea/data/dataV1.csv'

# South korea census data.
# source: https://www.populationpyramid.net/republic-of-korea/2019/
_SK_CENSUS_PATH = '../SouthKoreaCensus/data/data.csv'

# Path to U.S. census data.
_CENSUS_PATH = '../US_Census/data/data.csv'

# Path to U.S. JSON
_US_DATA_PATH = 'data.json'

# Reads the South Korea data.
#
# return: np.array([float]) (length 90 array, where covid_dist_ex[i] is the
#                            fraction of cases for age i)
def get_sk_covid_dist():
    # Step 1: Read data
    df = pd.read_csv(_SK_PATH)

    # Step 2: Extract data
    cols = ['Age_0s_Confirmed', 'Age_10s_Confirmed', 'Age_20s_Confirmed', 'Age_30s_Confirmed', 'Age_40s_Confirmed', 'Age_50s_Confirmed', 'Age_60s_Confirmed', 'Age_70s_Confirmed', 'Age_80s_Confirmed']
    covid_dist = []
    for i, col in enumerate(cols):
        covid_dist.append(df[col][_SK_IND])

    # Step 3: Normalize distribution
    covid_dist = np.array(covid_dist, dtype=np.float)
    covid_dist /= np.sum(covid_dist)

    # Step 4: Extrapolate to all age years
    covid_dist_ex = np.zeros([MAX_AGE+1])
    for i, val in enumerate(covid_dist):
        covid_dist_ex[10*i:10*(i+1)] = val/10

    return covid_dist_ex

# Returns the South Korea census data.
#
# return: np.array([float]) (length 90 array, where age_dist_ex[i] is the
#                            fraction of people of age i)
def get_sk_age_dist():
    # Step 1: Read data
    df = pd.read_csv(_SK_CENSUS_PATH)

    # Step 2: Extract data
    age_dist_ex = np.zeros([MAX_AGE+1])
    for gender in ['M', 'F']:
        for i, val in enumerate(df[gender][:-3]):
            for age in range(5*i, 5*(i+1)):
                age_dist_ex[age] += val / 5

    # Step 3: Normalize data
    age_dist_ex = age_dist_ex / np.sum(age_dist_ex)

    return age_dist_ex

# Reads the U.S. census data for the given state.
#
# state: str (e.g., 'MI')
# return: np.array([float]) (length 90 array, where age_dist_ex[i] is the
#                            fraction of people of age i)
def get_us_age_dist(state):
    # Step 1: Read data
    df = pd.read_csv(_CENSUS_PATH)

    # Step 2: Restrict to state
    df = df[df['state'] == state]

    # Step 3: Extract data
    cols = ['Under 5 years', '5 to 9 years', '10 to 14 years', '15 to 17 years', '18 and 19 years', '20 years', '21 years', '22 to 24 years', '25 to 29 years', '30 to 34 years', '35 to 39 years', '40 to 44 years', '45 to 49 years', '50 to 54 years', '55 to 59 years', '60 and 61 years', '62 to 64 years', '65 and 66 years', '67 to 69 years', '70 to 74 years', '75 to 79 years', '80 to 84 years', '85 years and over']
    age_dist = []
    for i, col_part in enumerate(cols):
        val = 0
        for gender in ['Male', 'Female']:
            col = '{}: {}'.format(gender, col_part)
            val += int(df[col].iloc[0])
        age_dist.append(val)

    # Step 4: Normalize distribution
    age_dist = np.array(age_dist, dtype=np.float)
    age_dist /= np.sum(age_dist)

    # Step 5: Extrapolate to all age years
    age_ranges = [range(5), range(5, 10), range(10, 15), range(15, 18), range(18, 20), range(20, 21), range(21, 22), range(22, 25), range(25, 30), range(30, 35), range(35, 40), range(40, 45), range(45, 50), range(50, 55), range(55, 60), range(60, 62), range(62, 65), range(65, 67), range(67, 70), range(70, 75), range(75, 80), range(80, 85), range(85, MAX_AGE+1)]
    age_dist_ex = []
    for val, age_range in zip(age_dist, age_ranges):
        for _ in age_range:
            age_dist_ex.append(val / len(age_range))
    age_dist_ex = np.array(age_dist_ex)

    return age_dist_ex

# Read and return the JSON data
#
# return: JSON data
def get_us_data():
    f = open(_US_DATA_PATH)
    line = f.readline().strip()
    f.close()
    return json.loads(line)

# Uncensor the given Covid case counts.
#
# covid_age_counts: [(int, int, int)] (tuples of min_age, max_age, and count for that range)
# uncensoring_ind: int (which bucket to use to uncensor the data)
# return: (np.array([n_buckets]), np.array([n_buckets])) (the uncensored Covid case counts)
def uncensor_covid_counts(covid_age_counts, age_dist, uncensoring_ind):
    # Step 1: Get South Korea distributions
    covid_dist_sk_raw = get_sk_covid_dist()
    age_dist_sk = get_sk_age_dist()

    # Step 2: Build counts for the current distribution
    covid_counts = [count for _, _, count in covid_age_counts]
    covid_counts = np.array(covid_counts, dtype=np.float)

    # Step 3: Build bins for the South Korea distribution
    covid_dist_sk = np.zeros(covid_counts.shape)
    for i, (min_age, max_age, _) in enumerate(covid_age_counts):
        for age in range(min_age, max_age+1):
            covid_dist_sk[i] += covid_dist_sk_raw[age]

    # Step 4: Compute the uncensoring constant based on the highest age bucket
    uncensoring_const = covid_counts[uncensoring_ind] / covid_dist_sk[uncensoring_ind]

    # Step 5: Build bins for South Korea age distribution
    age_dist_sk_bin = np.zeros(covid_counts.shape)
    for i, (min_age, max_age, _) in enumerate(covid_age_counts):
        for age in range(min_age, max_age+1):
            age_dist_sk_bin[i] += age_dist_sk[age]

    # Step 6: Build counts for U.S. age distribution
    age_dist_bin = np.zeros(covid_counts.shape)
    for i, (min_age, max_age, _) in enumerate(covid_age_counts):
        for age in range(min_age, max_age+1):
            age_dist_bin[i] += age_dist[age]

    # Step 7: Compute the censored and uncensored counts
    covid_counts_censored = covid_counts
    covid_counts_uncensored = uncensoring_const * covid_dist_sk * age_dist_bin / age_dist_sk_bin

    return covid_counts_censored, covid_counts_uncensored

# Uncensor the given Covid case counts for the given state.
#
# state_code: str
# age_ranges: [(int, int)] (list of age ranges for each column in cols)
# us_data: JSON data (obtained using get_us_data above)
# uncensoring_ind: int (which column to use to uncensor, typically the last one)
def uncensor_covid_counts_state_helper(state_code, age_ranges, us_data, uncensoring_ind):
    # Step 1: Build age ranges
    cols = []
    for min_age, max_age in age_ranges[:-1]:
        cols.append('# Cases Age [{}-{}]'.format(min_age, max_age))
    cols.append('# Cases Age [{}+]'.format(age_ranges[-1][0]))

    # Step 2: Run uncensoring for each date
    results = {}
    for state_data in us_data['USA'][state_code]:
        try:
            # Step 2a: Extract counts
            covid_age_counts = []
            for col, (min_age, max_age) in zip(cols, age_ranges):
                count = state_data[col]
                covid_age_counts.append((min_age, max_age, count))

            # Step 2b: Age counts
            covid_counts = np.array([count for _, _, count in covid_age_counts], dtype=np.float)

            # Step 2c: Age distribution
            age_dist = get_us_age_dist(state_code)

            # Step 2d: Run uncensoring
            covid_counts_censored, covid_counts_uncensored = uncensor_covid_counts(covid_age_counts, age_dist, uncensoring_ind)

            # Step 2e: Get scrape time
            scrape_time = state_data['Scrape Time']

            # Step 2f: Compute current result
            results[scrape_time] = (np.sum(covid_counts_uncensored), np.sum(covid_counts_censored), np.sum(covid_counts_uncensored) / np.sum(covid_counts_censored))

        except:
            pass

    # Step 3: Strip time from reading
    results_processed = {}
    for scrape_time, result in results.items():
        # Step 3a: Obtain the date
        scrape_date = scrape_time.split()[0]
 
        # Step 3b: Ignore dates already processed
        if scrape_date in results_processed:
            continue

        # Step 3c: Update results
        results_processed[scrape_date] = result

    return results

# Uncensor the given Covid case counts for the given state.
#
# state_code: str
# all_age_ranges: [[(int, int)]] (list of age ranges for each column in cols)
# us_data: JSON data (obtained using get_us_data above)
# uncensoring_ind: int (which column to use to uncensor, typically the last one)
# return: {str: (float, float, float)} (map from date to uncensored counts, censored counts, and ratio)
def uncensor_covid_counts_state(state_code, all_age_ranges, us_data, uncensoring_ind):
    results = {}
    for age_ranges in all_age_ranges:
        results.update(uncensor_covid_counts_state_helper(state_code, age_ranges, us_data, uncensoring_ind))
    return results

# Uncensor the given Covid case counts for the given state, using default parameters
#
# state_code: str (postal code of state, e.g., 'NY')
# all_age_ranges: [[(int, int)]]
# us_data: JSON data (obtained using get_us_data above)
# fn_process_results: {str: (float, float, float)} * JSON data -> {str: (float, float, float)} (preprocessing function)
def run_state_helper(state_code, all_age_ranges, us_data, fn_process_results=None):
    # Step 1: Get results
    uncensoring_ind = -1
    results = uncensor_covid_counts_state(state_code, all_age_ranges, us_data, uncensoring_ind)

    # Step 2: Preprocess results
    if not fn_process_results is None:
        results = fn_process_results(us_data, results)

    # Step 3: Printing
    print(state_code)
    dates = []
    counts = []
    uncensored_counts = []
    for date in sorted(results.keys()):
        result = results[date]
        print(date, result)
        dates.append(date.split()[0])
        counts.append(result[1])
        uncensored_counts.append(result[0])

    # Step 4: Plotting
    date_skip = 14
    plt.plot(dates, counts, label='Reported')
    plt.plot(dates, uncensored_counts, label='Ours')
    plt.xticks(list(range(0, len(dates), date_skip)), dates[::date_skip])
    plt.xlabel('Date')
    plt.ylabel('# Cases')
    plt.ylim(bottom=0.0)
    plt.legend()
    plt.tight_layout()
    plt.savefig('{}.png'.format(state_code))
    plt.clf()

# Uncensor the given Covid case counts for the given state, using default parameters
#
# state_code: str (postal code of state, e.g., 'NY')
# all_age_ranges: [[(int, int)]]
def run_state(state_code, all_age_ranges, fn_process_results=None):
    us_data = get_us_data()
    run_state_helper(state_code, all_age_ranges, us_data, fn_process_results)
