import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 17), (18, 40), (41, 60), (61, 80), (80, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('IA', all_age_ranges)