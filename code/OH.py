import os
import datetime

# To download the docx file, run a command along the following lines:
#
# curl https://www.mass.gov/doc/covid-19-cases-in-massachusetts-as-of-march-27-2020-accessible/download > 3-27-20.docx
#
# For some reason, docx files were not available for some dates. Then, run the following command to get the PDF instead:
#
# curl https://www.mass.gov/doc/covid-19-cases-in-massachusetts-as-of-march-27-2020/download > 3-27-20.pdf

def run_OH(args):
    day, month, year = args['day'], args['month'], args['year']
    cmd = 'curl https://coronavirus.ohio.gov/static/COVIDSummaryData.csv > ../OH/raw/{}-{}-{}.csv'.format(month, day, year)
    os.system(cmd)

if __name__ == '__main__':
    day = datetime.datetime.today().day
    month = datetime.datetime.today().month
    year = datetime.datetime.today().year - 2000
    args = {'day': day, 'month': month, 'year': year}
    run_OH(args)
