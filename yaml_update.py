#!/usr/local/bin/python3

import yaml
import argparse
import dpath.util


def is_yaml(file):
    """
    Check if file is valid YAML.
    """
    if yaml.safe_load(file):
        return True
    else:
        print('Provide valid YAML.')
        exit(1)


def key_exists(config, key):
    """
    Check if key path exists.
    """
    try:
        dpath.util.get(config, key)
    except Exception:
        return False
    return True


# Get location of yaml file and yaml key/value to udpate.
parser = argparse.ArgumentParser(
    description="Update a key value in-place within YAML file."
)
parser.add_argument('key',
                    help='set the key to update, path separated by /, '
                    'for example, to update key "a:b:c", use "a/b/c"',
                    type=str)
parser.add_argument('value', help='set the value to update', type=str)
parser.add_argument('file', help='set the location of yaml file', type=str)
args = parser.parse_args()

# Assign argument values to variables.
yaml_key = args.key
new_value = args.value
file_name = args.file

# Open file and load YAML into dictionary.
try:
    with open(file_name) as f:
        if is_yaml(f):
            f.seek(0)
            config = yaml.load(f, Loader=yaml.FullLoader)
except (IOError, EOFError) as err:
    print(err)
    exit(1)

# Apply overlay on existing configuration.
if key_exists(config, yaml_key):
    dpath.util.set(config, yaml_key, new_value)
    print('Updated key {}'.format(yaml_key))
else:
    try:
        dpath.util.new(config, yaml_key, new_value)
    except dpath.exceptions.PathNotFound:
        print('Key path not found in YAML.')
        exit(1)
    print('Added new key {}'.format(yaml_key))

# Update YAML file in-place.
try:
    with open(file_name, 'w') as f:
        yaml.dump(config, stream=f, default_flow_style=False, sort_keys=False)
except (IOError, EOFError) as err:
    print(err)
    exit(1)
