import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 4), (18, 35), (36, 49), (50, 64), (5, 17), (65, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('OK', all_age_ranges)