import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 60), (61, 70), (71, 80), (80, 89)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('TN', all_age_ranges)
