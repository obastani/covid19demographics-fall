import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 17), (18, 44), (45, 64), (65, 74), (75, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('NY', all_age_ranges)
