#!/bin/bash

# Script for restoring a MongoDB database from a backup
# Usage: mongorestore.sh <backup_dir> <target_db>
# <backup_dir> must be set to the top-level directory named with the timestamp of the backup

set -e

if [ -z "$1" ] || [ ! -d "$1" ]; then
  >&2 echo "Error: Backup directory must be specified"
  exit 1
fi

BACKUP_DIR=$1

if [ ! -f "$BACKUP_DIR/mongodump.log" ]; then
  >&2 echo "Error: Backup dir does not contain a mongodump.log file - is it a valid backup?"
  exit 1
fi

if [ -z "$2" ]; then
  >&2 echo "Error: Target database name must be specified"
  exit 1
fi

RESTORE_DB=$2

if [ -z "$MONGO_BACKUP_PWD" ]; then
  >&2 echo "Error: Password for MongoDB backup account not set (MONGO_BACKUP_PWD)"
  exit 1
fi

set +e

echo "Restoring from \"$BACKUP_DIR\""
LOGFILE=mongorestore-$(date "+%Y-%m-%d-%H-%M").log
cd $BACKUP_DIR
# TODO: Make nsFrom configurable
# NOTE: Can also pass --dryRun to test the restore command without importing any data
set -vo pipefail
echo $MONGO_BACKUP_PWD | mongorestore -u backup --authenticationDatabase admin --nsFrom "dicom.*" --nsTo "$RESTORE_DB.*" --gzip --stopOnError . 2>&1 | tee $LOGFILE
PEXIT=$?
set +vo pipefail
cd ..

if [ $PEXIT -eq 0 ]; then
  echo -e "\n--- Completed without error ---\n" | tee -a $BACKUP_DIR/$LOGFILE
  exit 0
fi

echo -e "\n!!! Completed with error !!!\n" | tee -a $BACKUP_DIR/$LOGFILE
exit 1

