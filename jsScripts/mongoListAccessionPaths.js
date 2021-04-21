/* MongoDB script that prints the DirectoryPath down to accession directory level in MongoDB's
   series collection to a list of format year/month/day.
   This list is used for the discovery of data gaps by comparison with a list of paths
   available in PACS. 

   To run:
       For default year ranges (2010-2018):
           mongo --quiet listAccessionPathsList.js > accessionPaths.json

       For custom year ranges:
           mongo --quiet --eval "var minYear=YYYY; var maxYear=YYYY" countByDay.js > counts.json

   Structure:
       {collection: {year: {month: {day: [DicomFilePath count, StudyDate count]}}}

   Log:
       2019-11-29 - BP - Create dictionary initialisation function
                       - Create count function
                       - Create prepend and monthly day count functions
*/
const DB_NAME = "dicom";
const CONN = new Mongo();
CONN.getDB("").auth("", "");  // enter authorisation details

var db = CONN.getDB(DB_NAME);
var counts = {};

function initDict() {
    var min = (typeof minYear === "undefined") ? 2010 : minYear;
    var max = (typeof maxYear === "undefined") ? 2018 : maxYear;

    for (year = min; year <= max; year++) {
        counts[year] = {};

        for (month = 1; month <= 12; month++) {
            var monthKey = prependZero(month);
            var noDays = daysInMonth(year, month);

            counts[year][monthKey] = {};

            for (day = 1; day <= noDays ; day++) {
                var dayKey = prependZero(day);
                counts[year][monthKey][dayKey] = [];
            }
        }
    }
}

function count() {
    var dbColl = db.getCollection("series");

    for (var year in counts) {
        for (var month in counts[year]) {
            for (var day in counts[year][month]) {
                var accession_numbers = [];

                dbColl.find({"header.DirectoryPath": {$regex: "^" + year + "/" + month + "/" + day}}).forEach(function(doc) {
                    accession_numbers.push(doc.header.DirectoryPath.split("/").pop());
                });

                counts[year][month][day] = (Array.from(new Set(accession_numbers))).sort();
            }
        }
    }
    printjson(counts);
}

function prependZero(number) {
    return (number <= 9) ? ("0" + number.toString()) : number.toString();
}

function daysInMonth(year, month) {
    return new Date(year, month, 0).getDate();
}

initDict();
count();