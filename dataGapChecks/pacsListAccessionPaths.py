''' Stand-alone script for producing a json file of all paths down to accession directory level.
                                                                               
    Log:
        2020-01-08 - DSM - Create main script (see pacscounter-0.1.py)
        2020-01-13 - BP - Add help utility with -min -max -o                                   
                        - Cleanup (spacing, indentation, structures)
'''          
import argparse                      # Terminal arguments and help utility
import os# Listing directory contents
import json# Writing output file
import multiprocessing               # Running counts in parallel                            
import datetime# Printing timestamps
from collections import OrderedDict  # Ensures output json file is in a particular order 
           
parser = argparse.ArgumentParser()
parser.add_argument("--minyear", "-min", help = "Minimum for range of years to be checked. Default to 2010.", type = int)      
parser.add_argument("--maxyear", "-max", help = "Maximum for range of years to be checked. Default to 2010.", type = int)
parser.add_argument("--outpath", "-o", help = "Output file path. Default to current/counts/.", type = str)
                    
# Constants
## Path to PACS directory containing the year/month/day structure
PACS_DIR="/beegfs-hdruk/extract/v12/PACS"                                                                  
                                                                                                       
def print_timestamped(string):                                                                                                 
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("[" + timestamp + "] " + string)
                                                                                   
def daycount(month_path):             
    """Returns dictionary of the number of DICOM files in each day of the given month"""
    days_dict = OrderedDict()
    print_timestamped("Process " + str(os.getpid()) + " checking directory: " + str(month_path))

    if os.path.exists(month_path):
        # Loop over each day subdirectory in this month
        days = os.listdir(month_path)                                                          
        days.sort()  # Sort into [01, 02, 03 ... ] order to ensure consistent output.
       
        for day in days:                       
            day_path = os.path.join(month_path, day)
                                 
            if os.path.isfile(day_path):    
                print_timestamped("WARNING! Ignoring file " + day_path + ".")
                continue                                                             
                                                                  
            # Loop over each accession number/study directory in this day
            study_paths = []                                           

            for study in os.listdir(day_path):
                study_path = os.path.join(day_path, study)                                                                     

                # Check this is a directory before attempting to list
                if os.path.isfile(study_path):
                    print_timestamped("WARNING! Ignoring file " + study_path + ".")
                    continue                 
                                         
                study_paths.append(study)
                         
            # Dictionary of counts per day for this month
            days_dict[day] = sorted(list(set(study_paths)))                        
    else:
        print_timestamped(str(month_path) + " does not exist. Setting count for this month to 0.")

    return days_dict

if __name__ == '__main__':                                                                                                     
    args = parser.parse_args()

    MIN_YEAR = 2010 if args.minyear is None else args.minyear
    MAX_YEAR = 2019 if args.maxyear is None else args.maxyear

    ## Range of years/subdirectories to be checked
    YEAR_RANGE=range(MIN_YEAR, MAX_YEAR)

    if args.outpath is None:
        OUTPUT_PATH = "study_paths.json"
    else:
    OUTPUT_PATH = args.outpath

    # Set up multiprocessing pool with 12 processes - 1 process per month, per year
    pool = multiprocessing.Pool(processes=12)

    # Get study/directory counts for each month in each year
    years_dict = OrderedDict()

    for year in YEAR_RANGE:
        year = str(year)  # Convert to string for use in paths and outputs
        month_dict=OrderedDict()  # For storing counts for each month in this year

        # Generate list of paths to be checked for each month in this year
        month_paths = []
        for month in range(1,13):
            month = "%02d" % month  # Pad single digit months with 0, e.g. 1 -> 01.
            month_path = os.path.join(PACS_DIR, year, month)
            month_paths.append(month_path)

        # Parallelise check over multiple processes, 1 process per month
        days_dicts = pool.map(daycount, month_paths)
        print_timestamped("Completed processing for year " + str(year) + ".")

        # Record results in expected dictionary format for output
        for month_index in range(1,13):
            month = "%02d" % month_index  # Pad as before
            month_dict[month] = days_dicts[month_index-1]

        # Completed loop over this month, add results to overall year dictionary
        years_dict[year] = month_dict

    # Complete loop over all years, write out final output file
    with open(OUTPUT_PATH, "w") as outputfile:
        json.dump(years_dict, outputfile, indent=4)  # Make human-readable with indent=4

    print_timestamped("Finished count and written output file.")