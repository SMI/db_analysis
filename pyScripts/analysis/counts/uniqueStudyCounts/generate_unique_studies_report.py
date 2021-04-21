''' Script that compares storage and MongoDB unique StudyInstanceUID counts and creates a report of format .md.

    Prerequisites:
        - python 3
        - json file of the latest general storage counts
        - json file of the latest unique StudyInstanceUID Mongo counts (extracted via /counts/queries/countUniqueStudies.js)

    This document includes:
        - date of reporting
        - comparison between daily storage and MongoDB counts of documents with unique StudyInstanceUIDs

    For help:
        python3 generate_unique_studies_report.py -h

    Log:
        2020-01-15 - BP - Create base detailed report generator based on generate_report v0.2
        2020-02-25 - BP - Add comments, add conditions on arguments and fix a bug
'''

import json
import argparse
from datetime import datetime

NOW = datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument("--storage", "-s", help = "Path to the general storage counts file", type = str, required=True)
parser.add_argument("--mongo", "-m", help = "Path to the unique StudyInstanceUID Mongo counts file", type = str, required=True)
parser.add_argument("--report", "-r", help = "Path to the report file", type = str, required=False)

def import_counts(path):
    '''Imports counts from .json files into a Python json object'''
    with open(path) as counts_file:
    counts_json = json.load(counts_file)

    return counts_json

def start_report():
    '''Creates the report file and initialises it with a title and timestamp of the report creation.
       The file name format is "countReport-YYYY_MM_DD.md".
    '''
    with open(REPORT_NAME, "w") as report_file:
        report_header = ("# Storage VS MongoDB count of unique StudyInstanceUID Report\n")
        report_header += ("### Performed on: {0}/{1}/{2} at {3}:{4}:{5}\n").format(
                          NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute, NOW.second)

        report_file.write(report_header)

def write_to_report(report_text):
    '''Appends text to the report created and initialised by start_report().'''
    with open(REPORT_NAME, "a") as report_file:
        report_file.write(report_text)
        print("save to file successful...")

def daily_counts():
    '''Creates a table of daily counts for the comparison of storage counts with MongoDB counts
       based on the StudyDate tag and the DicomFilePath tag.
    '''
    report_text = "\n### Please note that these counts have been performed based on the DicomFilePath tag\n"
    report_text += "| Year | Month | Day | Storage Count | MongoDB unique StudyInstanceUID |\n"
    report_text += "| ---- | ----- | --- | ------------- | ------------------------------- |\n"

    for year in MONGO_COUNTS:
        report_text += ("| {0} |").format(year)

        for month in MONGO_COUNTS[year]:
            if month == "01":
                report_text += (" {0} | ").format(month)
            else:
                report_text += ("| | {0} | ").format(month)

            for day in MONGO_COUNTS[year][month]:
                mongo_count = 0

                if day == "10":
                    report_text += ("{0} ").format(day)
                else:
                    report_text += ("| | | {0} ").format(day)

                mongo_count += MONGO_COUNTS[year][month][day]

                report_text += ("| {0} | {1} |\n").format(STORAGE_COUNTS[year][month][day], mongo_count)

    print("writing to md file...")
    write_to_report(report_text)


if __name__ == '__main__':
    print("starting script...")
    args = parser.parse_args()

    print("importing storage counts...")
    STORAGE_COUNTS = import_counts(args.storage)
    print("importing mongo counts...")
    MONGO_COUNTS = import_counts(args.mongo)

    if args.report is None:
        REPORT_NAME = ("countUniqueStudiesReport-{0}-{1}-{2}_{3}:{4}:{5}.md").format(
                       NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute, NOW.second)
    else:
        REPORT_NAME = args.report

    print("starting report...")
    start_report()
    print("starting table...")
    daily_counts()