#!/bin/bash

# Script for taking a backup of the MongoDB dicom database

set -e

if [ -z $MONGO_BACKUP_PWD ]; then
  >&2 echo "Error: Password for MongoDB backup account not set (MONGO_BACKUP_PWD)"
  exit 1
fi

BACKUP_DIR=$(date "+%Y-%m-%d-%H-%M")
LOGFILE=$BACKUP_DIR/mongodump.log

if [ -d "$BACKUP_DIR" ]; then
  >&2 echo "Error: Backup directory \"$BACKUP_DIR\" already exists"
  exit 1
fi

mkdir -p $BACKUP_DIR

# Can also specify a single collection with -c <coll>
echo $MONGO_BACKUP_PWD | mongodump -u backup --authenticationDatabase admin -d dicom --gzip -o $BACKUP_DIR > $LOGFILE 2>&1
echo -e "\n--- Completed without error ---\n" >> $LOGFILE

