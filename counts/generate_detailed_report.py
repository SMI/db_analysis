''' Script that compares storage and MongoDB counts and creates a report of format .md.

    This document includes:
        - date of reporting
        - daily counts and comparison between storage counts and MongoDB counts based
          on two different tags

    For help:
        python3 generate_detailed_report.py -h

    Log:
        2020-01-13 - BP - Create base detailed report generator based on generate_report v0.2
'''

import json
import argparse
from datetime import datetime
from collections import OrderedDict

NOW = datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument("--storage", "-s", help = "Path to the storage counts file", type = str, required = True)
parser.add_argument("--mongo", "-m", help = "Path to the mongo counts file", type = str, required = True)
parser.add_argument("--report", "-r", help = "Path to the report file", type = str, required = False)

def import_counts(path):
    '''Imports counts from .json files into a Python json object'''
    with open(path) as counts_file:
        counts_json = json.load(counts_file)

    return counts_json

def sort_counts(counts):
    for collection in counts:
        counts[collection] = OrderedDict(sorted(counts[collection].items()))

    return counts

def start_report():
    '''Creates the report file and initialises it with a title and timestamp of the report creation.
       The file name format is "countReport-YYYY_MM_DD.md".
    '''
    with open(REPORT_NAME, "w") as report_file:
        report_header = "# Storage VS MongoDB Detailed Count Report\n"
        report_header += ("### Performed on: {0}/{1}/{2} at {3}:{4}:{5}\n").format(
                          NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute, NOW.second)

        report_file.write(report_header)


def write_to_report(report_text):
    '''Appends text to the report created and initialised by start_report().'''
    with open(REPORT_NAME, "a") as report_file:
        report_file.write(report_text)

def daily_counts():
    '''Creates a table of daily counts for the comparison of storage counts with MongoDB counts
       based on the StudyDate tag and the DicomFilePath tag.
    '''
    report_text = "\n## Daily Counts\n"
    report_text += "| Year | Month | Day | Storage Count | MongoDB DicomFilePath Count | MongoDB StudyDate Count |\n"
    report_text += "| ---- | ----- | --- | ------------- | --------------------------- | ----------------------- |\n"

    for year in STORAGE_COUNTS:
        report_text += ("| {0} |").format(year)

        for month in STORAGE_COUNTS[year]:
            if month == "01":
                report_text += (" {0} | ").format(month)
            else:
                report_text += ("| | {0} | ").format(month)

            for day in STORAGE_COUNTS[year][month]:
                mongo_path_count = 0
                mongo_study_count = 0

                if day == "01":
                    report_text += ("{0} ").format(day)
                else:
                    report_text += ("| | | {0} ").format(day)

                for collection in MONGO_COUNTS:
                    mongo_path_count += MONGO_COUNTS[collection][year][month][day][0]
                    mongo_study_count += MONGO_COUNTS[collection][year][month][day][1]

                report_text += ("| {0} | {1} | {2} |\n").format(STORAGE_COUNTS[year][month][day], mongo_path_count,
                                                                mongo_study_count)

    write_to_report(report_text)


if __name__ == '__main__':
    args = parser.parse_args()

    STORAGE_COUNTS = import_counts(args.storage)
    MONGO_COUNTS = import_counts(args.mongo)
    sort_counts(MONGO_COUNTS)

    if args.report is None:
        REPORT_NAME = ("reports/countDetailedReport-{0}-{1}-{2}_{3}:{4}:{5}.md").format(
                       NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute, NOW.second)
    else:
        REPORT_NAME = args.report

    start_report()
    daily_counts()