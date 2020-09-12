import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 17), (18, 49), (50, 64), (65, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('CA', all_age_ranges)
