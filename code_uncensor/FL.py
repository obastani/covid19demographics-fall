import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 4), (5, 14), (15, 24), (25, 34), (35, 44), (45, 54), (55, 64), (65, 74), (75, 84), (85, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('FL', all_age_ranges)