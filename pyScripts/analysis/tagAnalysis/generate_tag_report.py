''' Script that pulls MongoDB tag availability counts and creates a report of format .md.

    This document includes:
        - date of reporting
        - reported tag, modality and path date
        - total no. of tags matching the path date in the reported modality
        - total no. of tags containing reported tag from the above
        - percentage of tag availability based on the last two counts
        - top values of the tag and their proportions

    For help:
        python3 generate_tag_report.py -h

    Log:
        2020-02-05 - BP - Create report initialisation functions
                        - Add help utility with -m, -c, -t, -r, -y flags
                        - Create table creation function for monthly counts
                        - Create table creation function for yearly counts by tag
        2020-02-18 - BP - Sort tag counts and get the top 5 most available
'''

import json
import argparse
import operator
from datetime import datetime
from collections import Counter

NOW = datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument("--modality", "-m", help = "String of the modality to be reported - mandatory for info", type = str, required=True)
parser.add_argument("--tag", "-t", help = "String of the tag to be reported - mandatory for info", type = str, required=True)
parser.add_argument("--year", "-y", help = "String list of years to be reported - mandatory for info", type = str, required=True)
parser.add_argument("--counts", "-c", help = "Path to the tag counts - mandatory", type = str, required=True)
parser.add_argument("--report", "-r", help = "Path to the report file - optional", type = str)

def import_counts(path):
    '''Imports counts from .json files into a Python json object'''
    with open(path) as counts_file:
    counts_json = json.load(counts_file)

    return counts_json

def sort_dict(dictionary, sort_type):
    if sort_type == "asc":
        dictionary = sorted(dictionary.items(), key=operator.itemgetter(1))
    elif sort_type == "desc":
        dictionary = sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)

    return dictionary

def start_report(modality, tag, years):
    '''Creates the report file and initialises it with a title, timestamp of the report creation,
       modality, tag and years covered. The file name format is "tagAnalyisReport-YYYY_MM_DD.md".
    '''
    with open(REPORT_NAME, "w") as report_file:
        report_header = "# MongoDB Tag Analysis Report\n"
        report_header += ("### Performed on: {0}/{1}/{2} at {3}:{4}:{5}\n").format(
                             NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute, NOW.second)
        report_header += ("### Modality: {0}\n").format(modality)
        report_header += ("### Tag: {0}\n").format(tag)
        report_header += ("### Year(s): {0}\n").format(years)

        report_file.write(report_header)

def write_to_report(report_text):
'''Appends text to the report created and initialised by start_report().'''
    with open(REPORT_NAME, "a") as report_file:
    report_file.write(report_text)

def general_prop():
'''Creates a table of general proportion (by year) of MongoDB objects that contain the reported tag.
    '''
    report_text = "\n## Yearly proportion\n"
    report_text += "| Year | Total Count | Containing Tag | Availability Percentage |\n"
    report_text += "| ---- | ----------- | -------------- | ----------------------- |\n"

    for year in TAG_COUNTS:
        report_text += ("| {0} | ").format(year)
        total_count = 0
        tag_count = 0

        for month in TAG_COUNTS[year]:
            for day in TAG_COUNTS[year][month]:
                total_count += TAG_COUNTS[year][month][day]["total_count"]
                tag_count += TAG_COUNTS[year][month][day]["tag_count"]
                availability = str("{:.2%}".format(tag_count/total_count))

        report_text += ("{0} | {1} | {2} |\n").format(total_count, tag_count, availability)

    write_to_report(report_text)

def tag_values():
'''Creates a table of the top tag values and their proportion from the total number of objects that
       contain the tag.
    '''
    report_text = "\n## Most common values from those with the tag\n"
    report_text += "| Value | Documents with value |\n"
    report_text += "| ----- | -------------------- |\n"

    for year in TAG_COUNTS:
        overall_values = {}
        tag_count = 0

        for month in TAG_COUNTS[year]:
            for day in TAG_COUNTS[year][month]:
                if TAG_COUNTS[year][month][day]["values"] != 0:
                    overall_values = dict(Counter(overall_values) + Counter(TAG_COUNTS[year][month][day]["values"]))
                    tag_count += TAG_COUNTS[year][month][day]["tag_count"]

    overall_values = dict(sort_dict(overall_values, "desc")[:5])

    for value in overall_values:
        availability = str("{:.2%}".format(overall_values[value]/tag_count))

        report_text += ("| {0} | {1} |\n").format(value, availability)

    write_to_report(report_text)


if __name__ == '__main__':
    args = parser.parse_args()

    TAG_COUNTS = import_counts(args.counts)

    if args.report is None:
        REPORT_NAME = ("reports/tagAnalysisReport-{0}-{1}-{2}_{3}:{4}:{5}.md").format(
                       NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute, NOW.second)
    else:
        REPORT_NAME = args.report

    start_report(args.modality, args.tag, args.year)
    general_prop()
    tag_values()