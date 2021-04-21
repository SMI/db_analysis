'''List fields in a given MariaDb database.
   If given a modality, it lists the fields in tables that contain that modality in the name.
   This script outputs two files, a CSV list of the fileds in MariaDb and a copy of MongoDb
   tags with a flag indicator of whether they have been promoted to MariaDb or not.

   Usage:
      python3 maria_list_fields.py -m CT -a ct_mongo_tags.csv -p ct_maria_tags.csv
'''
import csv
import argparse
from modules.maria_lib import DbLib


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", "-d", help = "Name of MariaDb database. Default to data_load2.", type = str, required = False, default = "data_load2")
    parser.add_argument("--modality", "-m", help = "Modality name. (e.g. MR | CT). Default to all tables.", type = str, required = False, default="all")
    parser.add_argument("--available", "-a", help = "CSV list of available tags.", type = str, required = True)
    parser.add_argument("--processing", "-p", help = "Path for output list of processing tags.", type = str, required = True)

    return parser.parse_args()


def list_to_csv(in_list, out_path):
    with open(out_path, "w", newline="") as out_file:
        processing = csv.writer(out_file)
        processing.writerow(["Tag"])
        processing.writerows(in_list)


def check_processed(fields, available):
    '''Generates a copy of the available tags with an added flag
       to indicate whether the tag has been promoted to MariaDb
       or not.
    '''
    checklist_path = available.replace(".csv", "_checklist.csv")

    with open(available, 'r') as in_file, open(checklist_path, "w") as out_file:
        available = csv.DictReader(in_file)
        header = available.fieldnames

        header.append("Currently processing")
        checklist = csv.DictWriter(out_file, fieldnames=header)
        checklist.writeheader()

        for line in available:
            if line[header[0]] in fields:
                line["Currently processing"] = "True"
            else:
                line["Currently processing"] = "False"

            checklist.writerow(line)


def main(args):
    db = DbLib()
    db.use_db(args.database)
    tables = db.list_tables(args.modality)
    fields = []

    for table in tables:
        field_info_dict = db.get_table_field_info(table)

        for field in field_info_dict:
            fields.append(field)

    fields = sorted(list(set(fields)))
    list_to_csv([[field] for field in fields], args.processing)
    check_processed(fields, args.available)

    db.disconnect()


if __name__ == '__main__':
    args = argparser()
    main(args)