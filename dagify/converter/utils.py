# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import os
import pprint
import xml.etree.ElementTree as ET
import json
import yaml
from prettytable import PrettyTable


def clean_converter_type(converter_type):
    """Cleans a converter type string by removing all non-alphanumeric characters and converting it to uppercase.

    Args:
        converter_type (str): The converter type to clean.

    Returns:
        str: The cleaned converter type.
    """
    return re.sub("[^A-Za-z0-9]+", "", converter_type).upper()


def file_exists(file_path):
    """Checks if a file exists.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    file_path = os.path.abspath(file_path)
    return os.path.isfile(file_path)


def is_directory(folder_path):
    """Checks if a path is a directory.

    Args:
        folder_path (str): The path to the folder.

    Returns:
        bool: True if the path is a directory, False otherwise.
    """
    return os.path.isdir(folder_path)


def directory_exists(folder_path):
    """Checks if a folder exists.

    Args:
        folder_path (str): The path to the folder.

    Returns:
        bool: True if the folder exists, False otherwise.
    """
    return os.path.isdir(folder_path)


def create_directory(folder_path):
    """Creates a folder if it does not already exist.

    Args:
        folder_path (str): The path to the folder to create.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def read_yaml_to_dict(yaml_file):
    """Loads a YAML file into a dictionary.

    Args:
        yaml_file (str): The path to the YAML file.

    Returns:
        dict: The dictionary representation of the YAML file.
    """
    if yaml_file is None or not file_exists(yaml_file):
        raise FileNotFoundError(
            "dagify: template file provided is None or does not exist")
        return

    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)


def display_dict(dict):
    """Pretty prints a dictionary.

    Args:
        dict (dict): The dictionary to print.
    """
    pprint.pprint(dict)


def count_yaml_files(directory, case_sensitive=True, recursive=False):
    """
    Counts the number of YAML files (.yaml or .yml) in a directory.

    Args:
        directory (str): The path to the directory to search.
        case_sensitive (bool): Whether the search should be case-sensitive (default: True).
        recursive (bool): Whether to search subdirectories recursively (default: False).

    Returns:
        int: The number of YAML files found.
    """

    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if (case_sensitive and file.endswith(('.yaml', '.yml'))) or \
               (not case_sensitive and file.lower().endswith(('.yaml', '.yml'))):
                count += 1
        if not recursive:
            break  # Stop after the first level if not recursive

    return count


def generate_report(lines, title, columns, rows, warning_line, output_dir):
    """ Function to open a file and write the contents of the report in the file """
    report = PrettyTable()
    report.title = title
    i = 0
    # Column config
    report.field_names = columns
    for col in columns:
        report.align[col] = "l"

    # Row config
    report.add_rows(rows)

    report_file = f"{output_dir}/Detailed-Report.txt"
    with open(report_file, "w") as final_report:
        for line in lines:
            final_report.write(line + '\n')
        final_report.write(str(report) + '\n')
        final_report.write(warning_line)


def get_jobtypes_andcount(source_path):
    """Generic function that calculates the job_types and the count from any input"""
    unique_job_types = []
    job_types_source = []
    job_types_count = 0
    if source_path.endswith('.xml'):
        tree = ET.parse(source_path)
        root = tree.getroot()
        # Find all JOB elements
        job_elements = root.findall('.//JOB')
        # Extract TASKTYPE values and store them in a set to ensure uniqueness
        job_types_source = list({job.get('TASKTYPE') for job in job_elements})
        # Convert all to lowercase for comparision
        job_types_source = [item.lower() for item in job_types_source]
        unique_job_types = list(set(job_types_source))
        job_types_count = len(unique_job_types)
    elif source_path.endswith('config.yaml'):
        with open(source_path, 'r') as file:
            data = yaml.safe_load(file)
        for mapping in data['config']['mappings']:
            job_types_source.append(mapping['job_type'])

        # Convert all to lowercase for comparision
        job_types_source = [item.lower() for item in job_types_source]
        unique_job_types = list(set(job_types_source))
        job_types_count = len(unique_job_types)
    return unique_job_types, job_types_count


def format_table_data(title, columns, rows):
    """Formats table data into a JSON-friendly structure"""

    table_data = {
        "title": title,
        "columns": columns,
        "rows": []
    }

    for row in rows:
        row_dict = {}
        for col_index, value in enumerate(row):
            row_dict[columns[col_index]] = value
        table_data["rows"].append(row_dict)

    return table_data


def generate_json(statistics, table_data, output_file_path):
    """Creates a JSON file with intro text, table data, and conclusion text"""

    data = {
        "High_Level_Info": statistics,
        "table_data": table_data,
    }
    json_file_path = f"{output_file_path}/report.json"
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file, indent=2)  # indent for better readability
