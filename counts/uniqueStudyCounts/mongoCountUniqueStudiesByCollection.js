/* MongoDB script that counts the number of objects in MongoDB collection with a match on
   the DicomFilePath or StudyDate keys by collection -> year -> month -> day -> tag
   that have unique StudyInstanceUIDs. 

   To run:
       For default year ranges (2010-2010) and collection (CT):
           mongo --quiet countUniqueStudies.js > counts.json

       For custom year ranges and collection:
           mongo --quiet --eval "var minYear=YYYY; var maxYear=YYYY; var coll='image_MR'" countUniqueStudies.js > counts.json

   Structure:
       {collection: {year: {month: {day: [DicomFilePath count]}}}

   Log:
       2020-01-14 - BP - Create initial script with input start and end year
       2020-02-03 - BP - Add input for collection and default to CT
*/
const DB_NAME = "dicom";
const CONN = new Mongo();
CONN.getDB("").auth("", "");  // enter authorisation details

var db = CONN.getDB(DB_NAME);
var counts = {};

function initDict() {
    print("Initialising dictionary...");

    counts = {};
    var min = (typeof minYear === "undefined") ? 2010 : minYear;
    var max = (typeof maxYear === "undefined") ? 2018 : maxYear;

    for (year = min; year <= max; year++) {
        counts[year] = {};

        for (month = 12; month <= 12; month++) {
            var monthKey = prependZero(month);
            var noDays = daysInMonth(year, month);

            counts[year][monthKey] = {};

            for (day = 1; day <= noDays; day++) {
                var dayKey = prependZero(day);
                counts[year][monthKey][dayKey] = 0;
            }
        }
    }
}

function count() {
    var collection = (typeof coll === "undefined") ? "image_CT" : coll;
    var dbColl = db.getCollection(collection);

    for (var year in counts) {
        for (var month in counts[year]) {
            for (var day in counts[year][month]) {
                print("Printing " + year + "/" + month + "/" + day);

                var studyMatches = dbColl.distinct("StudyInstanceUID", {"header.DicomFilePath": {$regex: "^" + year + "/" + month + "/" + day}});
                var studyMatchesCount = studyMatches.length;

                print(studyMatchesCount);

                counts[year][month][day] = studyMatchesCount;
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