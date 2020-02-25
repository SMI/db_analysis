''' Script that takes in two lists of accession directory paths in form JSON: one from
    MongoDB and one from PACS and generates a list of the difference in form CSV.

    Sample run:
        python3 generate_detailed_report.py -m path_to_mongo_list.csv -s path_to_pacs_list.csv 

    For help:
        python3 generate_detailed_report.py -h

    Log:
        2020-01-14 - BP - Create base detailed report generator based on generate_report v0.2
'''

import json
import argparse
import csv
from datetime import datetime

NOW = datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument("--storage", "-s", help = "Path to the storage counts file", type = str, required=True)
parser.add_argument("--mongo", "-m", help = "Path to the mongo counts file", type = str, required=True)
parser.add_argument("--diff", "-d", help = "Path to the diff file. Default to untouched_accession_paths.csv", type = str, required=False)

def import_paths(filepath):
    '''Imports access directory paths from .json files into a Python json object'''
    with open(filepath) as paths_file:
    paths_json = json.load(paths_file)

    return paths_json

def extract_diffs():
    '''Creates a table of daily counts for the comparison of storage counts with MongoDB counts
       based on the StudyDate tag and the DicomFilePath tag.
    '''
    with open(REPORT_NAME, "a+") as final_list:
        print("Opened file...")

        for year in STORAGE_LIST:
            for month in STORAGE_LIST[year]:
                for day in STORAGE_LIST[year][month]:
                    print("Finding diff for {0}/{1}/{2}...".format(year, month, day))
                    storage_paths = STORAGE_LIST[year][month][day]
                    mongo_paths = MONGO_LIST[year][month][day]
                    paths = list(set(storage_paths) - set(mongo_paths))

                    for path in paths:
                        final_list.write("/beegfs-hdruk/extract/v12/PACS/" + year + "/" + month + "/" + day + "/" + path + ",\n")

if __name__ == '__main__':
    args = parser.parse_args()

    STORAGE_LIST = import_paths(args.storage)
    MONGO_LIST = import_paths(args.mongo)

    if args.diff is None:
        DIFF_NAME = ("untouched_accession_paths.csv")
    else:
        DIFF_NAME = args.diff

    extract_diffs()