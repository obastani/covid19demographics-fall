import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 5), (6, 19), (20, 29), (20, 44), (30, 39), (40, 49), (45, 64), (50, 59), (60, 69), (70, 79), (80, 89), (90, 99), (65, MAX_AGE), (70, MAX_AGE), (100, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('MN', all_age_ranges)