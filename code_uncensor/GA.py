import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 17), (18, 59), (60, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('GA', all_age_ranges)