import os
from util import *

if __name__ == '__main__':
    # Step 1: Read states
    f = open('states.txt')
    states = [line.strip() for line in f]
    f.close()

    # Step 2: Default parameters
    us_data = get_us_data()

    # Step 3: Run script for each state
    for state in states:
        # Step 3a: Ignore states without scripts
        if not os.path.exists('{}.py'.format(state)):
            continue

        # Step 3c: Get state data
        exec('from {} import run'.format(state))
        try:
            exec('from {} import process_results'.format(state))
        except:
            process_results = None
        all_age_ranges = run()

        # Step 3d: Run uncensoring
        run_state_helper(state, all_age_ranges, us_data, process_results)
