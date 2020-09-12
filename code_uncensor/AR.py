import numpy as np
from util import *

def run():
    all_age_ranges = [[(0, 17), (0, 18), (18, 24), (19, 64), (25, 44), (45, 64), (65, MAX_AGE)]]
    return all_age_ranges

if __name__ == '__main__':
    all_age_ranges = run()
    run_state('AR', all_age_ranges)