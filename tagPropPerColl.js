/* MongoDB script that returns the proportion of MongoDB objects from a specific collection
 * that contain a specific tag. 

    To run:
        For default collection (MR), tag (AngioFlag), start year (2010) and end year (2018):
            mongo tagPropPerColl.js > prop.txt

        For custom collection:
            mongo --eval "var coll='image_CT';" tagPropPerColl.js > prop.txt

        For custom tag:
            Edit script by adding tag name at lines 68, 71 and 73 instead of default "AngioFlag" 

        For custom start and end years:
            mongo --eval "var minYear=2016; var maxYear=2017;" tagPropPerColl.js > prop.txt

    Log:
        2020-02-03 - BP - Create initial script with default on MR, tag AngioFlag
        2020-02-04 - BP - Add aggregate for tag value counts
                        - Make use of custom tag names in queries (tested and not achieved)
                        - Is there a way to combine tagMatches and tagValues queries?
*/
const DB_NAME = "dicom";
const CONN = new Mongo();
CONN.getDB("").auth("", ""); // enter authorisation details

var db = CONN.getDB(DB_NAME);
var counts = {};

function initDict() {
    counts = {};
    var min = (typeof minYear === "undefined") ? 2010 : minYear;
    var max = (typeof maxYear === "undefined") ? 2018 : maxYear;

    for (year = min; year <= max; year++) {
        counts[year] = {};

        for (month = 1; month <= 1; month++) {
            var monthKey = prependZero(month);
            var noDays = daysInMonth(year, month);

            counts[year][monthKey] = {};

            for (day = 1; day <= noDays; day++) {
                var dayKey = prependZero(day);
                // day = [totalCount, tagCount]
                counts[year][monthKey][dayKey] = {
                    "total_count": 0,
                    "tag_count": 0,
                    "values": {}
                };
            }
        }
    }
}

function count() {
    var collection = (typeof coll === "undefined") ? "image_MR" : coll;
    var dbColl = db.getCollection(collection);

    for (var year in counts) {
        for (var month in counts[year]) {
            for (var day in counts[year][month]) {
                totalCount = 0;
                tagCount = 0;

                totalMatches = dbColl.find({"header.DicomFilePath": {$regex: "^" + year + "/" + month + "/" + day}});
                tagMatches = dbColl.find({"header.DicomFilePath": {$regex: "^" + year + "/" + month + "/" + day}, "AngioFlag": {"$exists": true}});
                tagValues = dbColl.aggregate([
                    { $match: { "header.DicomFilePath": {$regex: "^" + year + "/" + month + "/" + day}} },
                    { $match: { "AngioFlag" : {"$exists": true}} },
                    { $group: {
                            "_id": "$AngioFlag",
                            "count": {$sum: 1}
                        }
                    },
                    { $group: {
                            "_id": null,
                            "counts": { $push: {"k": "$_id", "v": "$count"} }
                        }
                    },
                    { $replaceRoot: { "newRoot": {$arrayToObject: "$counts"} }},
                    { $limit: 3 }
                ]);

                totalNo = totalMatches.count();
                tagNo = tagMatches.count();
                
                counts[year][month][day]["total_count"] += totalNo;
                counts[year][month][day]["tag_count"] += tagNo;
                counts[year][month][day]["values"] = tagValues.toArray()[0];
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
