#!/bin/bash 
: 'This script is meant to run through the following steps:
   1. MongoDB pre-deduplication accounting
   2. Pre-deduplication general and detailed reporting
   3. De-duplicating
   4. MongoDB post-deduplication accounting
   5. Post-deduplication general and detailed reporting

   The filepaths for these outputs are:
   1. -> counts/countsBeforeDedup
   2. -> reports/reportsBeforeDedup
   4. -> counts/countsAfterDedup
   5. -> reports/reportsAfterDedup

   This script is to be a cronjob for regular runs ensuring
   the storage counts have enough time to perform beforehand.

   Log:
   2020-01-13 - BP - The script meets steps one and two
                   - Automation not implemented due to unknown
                     time of storage counts (logs and output files
                     need to be preserved over time)
   2020-01-16 - BP - Add 3, 4 and 5
'
cd /nfs/smi/home/smi/MongoDbQueries/counts/

timestamp=`date "+%Y-%m-%d_%H:%M:%S"`
LOG="logs/${timestamp}.log"
bcounts="counts/countsBeforeDedup/mongoCounts-${timestamp}.json"
bgreport="reports/reportsBeforeDedup/countGeneralReport-${timestamp}.md"
bdreport="reports/reportsBeforeDedup/countDetailedReport-${timestamp}.md"

acounts="counts/countsAfterDedup/mongoCounts-${timestamp}.json"
agreport="reports/reportsAfterDedup/countGeneralReport-${timestamp}.md"
adreport="reports/reportsAfterDedup/countDetailedReport-${timestamp}.md"

function count() {
    timestamp=`date "+%Y-%m-%d_%H:%M:%S"`
    echo "Daily count start: ${timestamp}" >> $LOG
    mongo --quiet --eval "var maxYear = 2018;" queries/countByDay.js > $1

    timestamp=`date "+%Y-%m-%d_%H:%M:%S"`
    echo "Daily count end: ${timestamp}" >> $LOGppopp
}

function report() {
    timestamp=`date "+%Y-%m-%d_%H:%M:%S"`
    echo "Report start: ${timestamp}" >> $LOG
    python3 generate_report.py -s "/beegfs-hdruk/smi/data/counts/dicom_count.json" -m $3 -r $1
    python3 generate_detailed_report.py -s "/beegfs-hdruk/smi/data/counts/dicom_count.json" -m $3 -r $2

    timestamp=`date "+%Y-%m-%d_%H:%M:%S"`
    echo "Report end timestamp: ${timestamp}" >> $LOG
}

function deduplicate() {
    timestamp=`date "+%Y-%m-%d_%H:%M:%S"`
    echo "Deduplication start: ${timestamp}" >> $LOG
    mongo ../deduplication/deleteRepeatedByFilePath.js > ../deduplication/logs/${timestamp}.log

    timestamp=`date "+%Y-%m-%d_%H:%M:%S"`
    echo "Deduplicsation finish: ${timestamp}" >> $LOG
}

count $bcounts && report $bgreport $bdreport $bcounts && deduplicate && count $acounts && report $agreport $adreport $acounts