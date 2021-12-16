import requests
import json
import argparse
import math
from bs4 import BeautifulSoup

# Get location of coverage file on local disk.
parser = argparse.ArgumentParser(
    description='Extract and push coverage report to JIRA.'
)
parser.add_argument('jira_issue',
                    help='set link of JIRA issue',
                    type=str)
parser.add_argument('-f', '--file',
                    help='set the location of index.html file',
                    type=str,
                    default='coverage/lcov-report/index.html')
args = parser.parse_args()
issue = args.jira_issue
report_file = args.file


def range_finder(num):
    """ Return range based on the input number. """
    ranges = {
        range(0, 11): '0-10',
        range(11, 21): '11-20',
        range(21, 31): '21-30',
        range(31, 41): '31-40',
        range(41, 51): '41-50',
        range(51, 61): '51-60',
        range(61, 71): '61-70',
        range(71, 81): '71-80',
        range(81, 91): '81-90',
        range(91, 101): '91-100'
    }

    for key in ranges:
        if math.floor(num) in key:
            return ranges[key]
            break
    else:
        return '0-10'


def prepare_data(data_dict, coverage_dict, coverage_key, jira_field):
    """ Add coverage data to dict object. """
    if coverage_dict[coverage_key] > 80:
        data_dict['fields'][jira_field] = {
            "value": str(math.floor(coverage_dict[coverage_key]))
        }
    else:
        data_dict['fields'][jira_field] = {
            "value": range_finder(coverage_dict[coverage_key])
        }


with open(report_file) as source_file:
    soup = BeautifulSoup(source_file, 'html.parser')

# Find element with label 'class=clearfix'.
stats = soup.find('div', attrs={'class': 'clearfix'})

# Find all the div elements under 'class=clearfix'.
divs = stats.find_all('div')

# Create empty dict to hold coverage data.
coverage = {}

# Loop through div elements, split and add data to coverage dict.
for item in divs:
    coverage_line = item.text.splitlines()
    coverage[coverage_line[2]] = float(coverage_line[1].strip('% '))

# Prepare headers.
# Add base64 encoded API key for Basic authentication.
headers = {
    "Authorization":
    "Basic xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "Content-Type": "application/json"
}

# Prepare request body.
data = {'fields': {}}

# Add accurate coverage percentage values to request body.
data['fields']['customfield_10057'] = coverage['Statements']
data['fields']['customfield_10058'] = coverage['Branches']
data['fields']['customfield_10059'] = coverage['Functions']
data['fields']['customfield_10060'] = coverage['Lines']

# Add rounded coverage data to JIRA Select List.
# Send rounded single number if coverage is above 80%.
# Send range if coverage is below 80%.
prepare_data(data, coverage, 'Statements', 'customfield_10065')
prepare_data(data, coverage, 'Branches', 'customfield_10066')
prepare_data(data, coverage, 'Functions', 'customfield_10067')
prepare_data(data, coverage, 'Lines', 'customfield_10068')

# Serialize data to JSON object.
json_data = json.dumps(data)

# Push data to JIRA using API.
response = requests.put(issue, data=json_data, headers=headers)
