import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 1), (1, 14), (15, 24), (25, 44), (45, 64), (65, 84), (85, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('UT', all_age_ranges)
