#!/bin/bash
cd /beegfs-hdruk/smi/data/counts

cp dicom_counts.py dicom_counts.bak

# '-u' to disable output buffering so progress is written to log file more often
python -u pacscounter.py &> pacscounter.log
