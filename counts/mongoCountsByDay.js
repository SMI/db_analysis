/* MongoDB script that counts the number of objects in MongoDB with a match on
   the DicomFilePath or StudyDate keys by collection -> year -> month -> day -> tag. 

   To run:
       For default year ranges (2010-2010):
           mongo --quiet countByDay.js > counts.json

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
    db.getCollectionNames().forEach(function(collName) {
        if(collName === "series") { return; }

        counts[collName] = {};
        var min = (typeof minYear === "undefined") ? 2010 : minYear;
        var max = (typeof maxYear === "undefined") ? 2018 : maxYear;

        for (year = min; year <= max; year++) {
            counts[collName][year] = {};

            for (month = 1; month <= 12; month++) {
                var monthKey = prependZero(month);
                var noDays = daysInMonth(year, month);

                counts[collName][year][monthKey] = {};

                for (day = 1; day <= noDays; day++) {
                    var dayKey = prependZero(day);
                    counts[collName][year][monthKey][dayKey] = [0, 0];
                }
            }
        }
    });
}

function count() {
    for (var coll in counts) {
        var dbColl = db.getCollection(coll);

        for (var year in counts[coll]) {
            for (var month in counts[coll][year]) {
                for (var day in counts[coll][year][month]) {
                    var pathNo = 0;
                    var studyNo = 0;

                    pathMatches = dbColl.find({"header.DicomFilePath": {$regex: "^" + year + "/" + month + "/" + day}});
                    studyMatches = dbColl.find({"StudyDate": {$regex: "^" + year + month + day}});

                    pathNo = pathMatches.count();
                    studyNo = studyMatches.count();

                    counts[coll][year][month][day][0] += pathNo;
                    counts[coll][year][month][day][1] += studyNo;
                }
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