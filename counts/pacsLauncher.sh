#!/bin/bash
cd /beegfs-hdruk/smi/data/counts

timestamp=`date "+%Y-%m-%d_%H:%M:%S"`
log="logs/pacscounter-${timestamp}.log"
count="counts/dicomCounts-${timestamp}.json.bak"

# '-u' to disable output buffering so progress is written to log file more often
python -u pacscounter.py &> $log

cp dicom_counts.py $count