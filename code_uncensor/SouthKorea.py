import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 89)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('SouthKorea', all_age_ranges)
