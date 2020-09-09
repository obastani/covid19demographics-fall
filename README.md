# COVID 19 Demographics Dataset

This repository contains data regarding key COVID-19 metrics across 34 US States, Iceland and South Korea. This data was collected from online reports given by state authorities. This repository includes data for the fall; data for the summer is available [here](https://github.com/obastani/covid19demographics).

## Getting Started

The raw data was processed into a JSON file, where you can find all the data that has been collected. It is important to note that data from different states and different points in time may contain different reported metrics, as state authorities may have changed what they report with time. The JSON has been zipped, and can be found in /data/.

The raw data is also available. This can be found in /raw/. Different authorities report COVID-19 data differently, so the raw data may be in different formats (HTML, JSON, CSV, PNG, etc.)

## JSON Data Structure

The JSON follows the following structure:

	File {
		"USA":
			{
				"AR": [...],
				...
				"WY": [...]
			},
		"Intl.":
			{
				"Iceland": [...],
				"SouthKorea": [...]
			}
	}

Each state key within either "USA" or "Intl." keys is a list of dictionaries. Each dictionary in the list represents a record for the dataset for the state. 
Usually, each dictionary represents the data collected for a state on a specific day. However, that is not the norm, since there are cases, such as county data, where each record is a county instead of a date.

This JSON strucutre was chosen due to the asymmetric nature of the data being collected across different states, where different metrics are being reported. This JSON structure allows us to provide all of our data in one single file, without having to worry about structure.

The data structure can be better understood with the below example.

## Example

The following is an example of one record in DE.

	File {
		"USA": 
			{
				...
				"DE":
					[
						{
							"Total Recovered": 9,
							"# Cases Age [0-4]": 1,
							"# Cases Age [5-17]": 3,
							"# Cases Age [18-49]": 95,
							"# Cases Age [50-64]": 53,
							"# Cases Age [65+]": 62,
							"Total Hospitalized": 31,
							"Total Cases: Critical Condition": 8,
							"Total Cases: Male": 105,
							"Total Cases: Female": 109,
							"Scrape Time": 2020-03 29 09:35:54.580040,
							"Entry Creation Date": 2020-03-23 12:07:13.724000,
							"Edit Date": 2020-03 28 16:43:35.687000,
							"Report Date": 2020-03 28 16:45:00
						},
						...
					],
				...
			},
		...
	}
				
Keep in mind that this record is specific to DE, meaning that the fields in the example above are not necessarily in all the other states or even in another date in DE. This is all dependent on what the state authorities reported at the time of scrape (Scrape Time).

## Navigating the File

Within /key/ there is an.xlsx file with all the field names, mapped by state. There is a pivot table in the file that will help you navigate and see what fields are available for each states. Again, since states may have changed what metrics they report, the fields are not standardized within a state across time, necessarily.


## Updates

The data will be updated twice a week on Mondays and Thursdays around 12PM EST. The raw data will be updated once a week on Monday around 12PM EST.

## Contributors

This data is made available by:

Hamsa Bastani, Osbert Bastani, Andrew Chiang, Alex Miller, Armin Pourshafeie, John Silberholz.

