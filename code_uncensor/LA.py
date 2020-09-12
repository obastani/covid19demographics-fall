import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 17), (18, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70 , MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('LA', all_age_ranges)