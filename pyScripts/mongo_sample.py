'''Script for retrieving sample documents from a given collection.

    Usage:
    - For one sample from collection image_MR
        python3 sample.py -c image_MR -p outputs/sample.json
    - For two samples from collection image_MR
        python3 sample.py -c image_MR -p outputs/ -n 2
'''
import os
import argparse
import modules.file_lib as flib
from modules.mongo_lib import DbLib


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", "-c", help = "Name of MongoDB collection.", type = str, required = True)
    parser.add_argument("--path", "-p", help = "Path to directory or file for the query result.", type = str, required = True)
    parser.add_argument("--number", "-n", help = "Number of samples to extract. Default to 1.", type = int, required = False, default = 1)

    return parser.parse_args()


def main(args):
    col = args.collection
    path = args.path
    number = args.number
    filenames = []

    if os.path.isfile(path) or ".json" in path:
        filenames.append(path)
    elif os.path.isdir(path):
        for n in range(0, number):
            filename = os.path.join(path, f"sample_{col}_{n}.json")
            filenames.append(filename)

    db = DbLib()
    db.switch_db("analytics")

    samples = db.sample(col, number)
    files = 0

    for sample in samples:
        flib.json_dump(sample, filenames[files])
        files += 1

    db.disconnect()


if __name__ == '__main__':
    args = argparser()
    main(args)