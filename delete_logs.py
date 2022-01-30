#!/usr/bin/env python3
"""Delete logs from InsightOps."""

import requests
import sys
from ratelimit import limits, sleep_and_retry

API_KEY = 'xxxxxxxxxx-xxxxxxxx-xxxxxxxxx'
LOG_SET = 'log-set'
PREFIX = 'empty_log'
REGION = 'us'
ONE_MINUTE = 60
MAX_CALLS_PER_MINUTE = 30


def get_logs():
    """Get all logs and return them in a list."""

    headers = {'x-api-key': API_KEY}

    url = ("https://{}.rest.logs.insight.rapid7.com/"
           "management/logs".format(REGION))

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print('Reqeust for usage failed with following error:\n', err)
        sys.exit(1)

    return response.json()['logs']


def filter_logs(logs_to_filter):
    """
    Get logs based on specified parameter and return them in a list.
    """

    filtered_logs = []

    for log in logs_to_filter:
        # Filter logs where name starts with prefix and
        # log is part of LOG_SET
        if ((log['logsets_info']) and
           log['name'].startswith(PREFIX) and
           log['logsets_info'][0]['name'] == LOG_SET):

            filtered_log = {
                'id': log['id'],
                'name': log['name'],
                'logset': log['logsets_info'][0]['name']
            }
            filtered_logs.append(filtered_log)

    print('-----------------------------------------------------------')
    print('Number of logs to cleanup: {}'.format(len(filtered_logs)))
    print('-----------------------------------------------------------')

    return filtered_logs  


@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=ONE_MINUTE)
def make_delete_request(log_key):
    headers = {'x-api-key': API_KEY}
    url = ("https://{}.rest.logs.insight.rapid7.com/"
           "management/logs/{}".format(REGION, log_key))
    try:
        print('sending delete request to: {}'.format(url))
        req = requests.delete(url, headers=headers)
        req.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print('Reqeust for deletion failed with following error:\n', err)
        sys.exit(1)
    return


@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=ONE_MINUTE)
def make_usage_request(log_key):
    """Get log usage."""
    headers = {'x-api-key': API_KEY}
    url = ("https://{}.rest.logs.insight.rapid7.com/"
           "usage/organizations/logs/{}".format(REGION, log_key))

    try:
        req = requests.get(url, headers=headers)
        req.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print('Reqeust for usage failed with following error:\n', err)
        sys.exit(1)

    return req


def delete_logs(logs_not_required):

    for log in logs_not_required:
        usage_response = make_usage_request(log['id'])

        if not usage_response.json()['usage']['daily_usage']:
            print('Deleting log {} with id {} from {}'
                  .format(log['name'], log['id'], log['logset']))
            make_delete_request(log['id'])
        else:
            print('{} in {} is not empty'.format(log['name'], log['logset']))


if __name__ == '__main__':
    logs = get_logs()
    logs_to_delete = filter_logs(logs)
    delete_logs(logs_to_delete)
