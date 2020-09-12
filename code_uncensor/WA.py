import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 19), (20, 39), (40, 59), (60, 79), (80, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('WA', all_age_ranges)
