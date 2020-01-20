''' Script that compares storage and MongoDB counts and creates a report of format .md.

    This document includes:
        - date of reporting
        - monthly counts and comparison between storage counts and MongoDB counts based
          on two different tags
        - yearly counts and a transfer percentage from storage to MongoDB based on the
          two different tags

    For help:
        python3 generate_report.py -h

    Log:
        2019-11-28 - BP - Create report initialisation functions
                        - Add help utility with -s and -m flags
                        - Create table creation function for monthly counts
                        - Create table creation function for yearly counts by tag
        2020-01-13 - BP - Accept report path as arg and default to reports folder
                        - Add -r flag for report path arg
'''

import json# Importing mongo and storage counts
import argparse# Terminal arguments and help utility
from datetime import datetime# Output file timestamp time of reporting    
from collections import OrderedDict   # Sorting MongoDB imported counts

NOW = datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument("--storage", "-s", help = "Path to the storage counts file", type = str)
parser.add_argument("--mongo", "-m", help = "Path to the mongo counts file", type = str)
parser.add_argument("--report", "-r", help = "Path to the report file", type = str)

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
        report_header = "# Storage VS MongoDB Count Report\n"
        report_header += ("### Performed on: {0}/{1}/{2} at {3}:{4}:{5}\n").format(
                          NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute, NOW.second)

        report_file.write(report_header)

def write_to_report(report_text):
    '''Appends text to the report created and initialised by start_report().'''
    with open(REPORT_NAME, "a") as report_file:
        report_file.write(report_text)

# modify mongo counts to include both studydate counts and dicomfilepath counts
def monthly_counts():
    '''Creates a table of monthly counts for the comparison of storage counts with MongoDB counts
       based on the StudyDate tag and the DicomFilePath tag.
    '''
    report_text = "\n## Monthly Counts\n"
    report_text += "| Year | Month | Storage Count | MongoDB DicomFilePath Count | MongoDB StudyDate Count |\n"
    report_text += "| ---- | ----- | ------------- | --------------------------- | ----------------------- |\n"

    for year in STORAGE_COUNTS:
        report_text += ("| {0} | ").format(year)

        for month in STORAGE_COUNTS[year]:
            if month == "01":
                report_text += ("{0} | ").format(month)
            else:
                report_text += ("| | {0} | ").format(month)

            storage_count = 0
            mongo_path_count = 0
            mongo_study_count = 0

            for day in STORAGE_COUNTS[year][month]:
                storage_count += STORAGE_COUNTS[year][month][day]

                for collection in MONGO_COUNTS:
                    mongo_path_count += MONGO_COUNTS[collection][year][month][day][0]
                    mongo_study_count += MONGO_COUNTS[collection][year][month][day][1]

            report_text += ("{0} | {1} | {2} |\n").format(storage_count, mongo_path_count, mongo_study_count)

    write_to_report(report_text)

def yearly_counts():
    '''Creates two tables of yearly counts containing the percentage of files transfered from
       storage to MongoDB based on the counts of the StudyDate tag and the DicomFilePath tag.
    '''
    path_table = "\n## Yearly Counts by DicomFilePath tag\n"
    path_table += "| Year | Storage Count | MongoDB DicomFilePath Count | Transfer Percentage |\n"

    study_table = "\n## Yearly Counts by StudyDate tag\n"
    study_table += "| Year | Storage Count | MongoDB StudyDate Count | Transfer Percentage |\n"

    common = "| ---- | ------------- | ------------- | ------------------------------ |\n"
    path_table += common
    study_table += common

    for year in STORAGE_COUNTS:
        year_field = ("| {0} | ").format(year)

        storage_count = 0
        mongo_path_count = 0
        mongo_study_count = 0

        for month in STORAGE_COUNTS[year]:
            for day in STORAGE_COUNTS[year][month]:
                storage_count += STORAGE_COUNTS[year][month][day]

                for collection in MONGO_COUNTS:
                    mongo_path_count += MONGO_COUNTS[collection][year][month][day][0]
                    mongo_study_count += MONGO_COUNTS[collection][year][month][day][1]

        path_table += year_field + ("{0} | {1} | ").format(storage_count, mongo_path_count)
        #path_transfer_percentage = str("{:.2%}".format(mongo_path_count/storage_count))
        path_transfer_percentage = str("{:.7%}".format(mongo_path_count/storage_count))
        path_table += ("{0} |\n").format(path_transfer_percentage)

        study_table += year_field + ("{0} | {1} | ").format(storage_count, mongo_study_count)
        #study_transfer_percentage = str("{:.2%}".format(mongo_study_count/storage_count))
        study_transfer_percentage = str("{:.7%}".format(mongo_study_count/storage_count))
        study_table += ("{0} |\n").format(study_transfer_percentage)

    write_to_report(path_table)
    write_to_report(study_table)

def collection_counts():
    '''Creates a table of yearly counts by collection'''
    report_text = "\n## Collection Counts\n"
    report_text += "| Collection | Year | MongoDB DicomFilePath Count | MongoDB StudyDate Count |\n"
    report_text += "| ---------- | ---- | --------------------------- | ----------------------- |\n"

    for collection in MONGO_COUNTS:
        collection_count_text = ("| {0} |").format(collection)

        for year in MONGO_COUNTS[collection]:
            collection_count_text += ((" {0} ").format(year) if year == "2010" else ("| | {0} ").format(year))
            collection_count_path = 0
            collection_count_study = 0

            for month in MONGO_COUNTS[collection][year]:
                for day in MONGO_COUNTS[collection][year][month]:
                    collection_count_path += MONGO_COUNTS[collection][year][month][day][0]
                    collection_count_study += MONGO_COUNTS[collection][year][month][day][1]

            collection_count_text += ("| {0} |").format(collection_count_path)
            collection_count_text += (" {0} |\n").format(collection_count_study)

        report_text += collection_count_text

    write_to_report(report_text)

if __name__ == '__main__':
    args = parser.parse_args()

    STORAGE_COUNTS = import_counts(args.storage)
    MONGO_COUNTS = import_counts(args.mongo)
    sort_counts(MONGO_COUNTS)

    if args.report is None:
        REPORT_NAME = ("reports/countGeneralReport-{0}-{1}-{2}_{3}:{4}:{5}.md").format(
                       NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute, NOW.second)
    else:
        REPORT_NAME = args.report

    start_report()
    monthly_counts()
    yearly_counts()
    collection_counts()