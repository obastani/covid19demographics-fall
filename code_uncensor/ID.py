import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 17), (18, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (18, 49), (80, 89), (90, 99), (50, MAX_AGE), (80, MAX_AGE), (100, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('ID', all_age_ranges)