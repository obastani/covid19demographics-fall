import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 1), (10, 19), (1, 9), (20, 29), (30, 39), (40, 49), (50, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('TX', all_age_ranges)
