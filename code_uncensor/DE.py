import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 4), (5, 14), (0, 18), (15, 19), (19, 30), (20, 24), (25, 34), (31, 40), (35, 44), (41, 50), (45, 54), (51, 60), (55, 64), (61, 70), (65, 74), (71, 80), (75, 80), (70, MAX_AGE), (80, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('DE', all_age_ranges)