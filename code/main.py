import os
import traceback
import datetime

# Step 1: Arguments
day = datetime.datetime.today().day
month = datetime.datetime.today().month
year = datetime.datetime.today().year - 2000
args = {'day': day, 'month': month, 'year': year}

# Step 2: Read states
f = open('states.txt')
states = [line.strip() for line in f]
f.close()

# Step 3: Helper function
def ensure(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# Step 4: Run script for each state
failures = []
for state in states:
    # Step 4a: Ignore states without scripts
    if not os.path.exists('{}.py'.format(state)):
        continue
    # Step 4b: Create necessary directories
    ensure('../{}/raw'.format(state))
    ensure('../{}/data'.format(state))
    # Step 4c: Try to run state script
    try:
        exec('from {} import run_{}'.format(state, state))
        exec('run_{}(args)'.format(state), globals(), locals())
        print('Running {}: Success!'.format(state))
    except Exception as e:
        failures.append(state)
        print('Running {}: Failure!'.format(state))
        traceback.print_exc()
        print(e)

# Step 5: Print failed states
print('Failed states: {}'.format(', '.join(failures)))
