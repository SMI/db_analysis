'''Script for retrieving a list of unique tags from a collection.
'''
import argparse
import modules.file_lib as flib
from modules.mongo_lib import DbLib


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", "-d", help = "Name of MongoDB database. Default to analytics.", type = str, required = False, default = "analytics")
    parser.add_argument("--collection", "-c", help = "Name of MongoDB collection.", type = str, required = True)
    parser.add_argument("--filepath", "-f", help = "Path and name of JSON file for the query result.", type = str, required = True)

    return parser.parse_args()


def main(args):
    db = DbLib()
    db.switch_db(args.database)

    flib.json_dump(db.list_tags(args.collection), args.filepath)

    db.disconnect()


if __name__ == '__main__':
    args = argparser()
    main(args)