import os
import datetime

def run_WI(args):
    now = datetime.datetime.now()
    now = str(now).replace(' ', '_')
    cmd = 'curl https://www.dhs.wisconsin.gov/sites/default/files/styles/large/public/covid-19-age-chart.png?itok=husFVYO1 > ../WI/raw/age_{}.png'.format(now)
    print(cmd)
    os.system(cmd)
    cmd = 'curl https://www.dhs.wisconsin.gov/sites/default/files/styles/large/public/covid-19-gender-chart.png?itok=jlPjRKqa > ../WI/raw/gender_{}.png'.format(now)
    print(cmd)
    os.system(cmd)

if __name__ == '__main__':
    run_WI({})
