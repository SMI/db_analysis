/* MongoDB script that checks the existence of a DicomFilePath of structure "yyyy/mm/dd/accession_no"
 * accross all collections apart from series. 

   To run:
       For default DicomFilePath (2016/01/01/E-05452050):
           mongo --quiet checkAccessionDir.js

       For custom DicomFilePath:
           mongo --quiet --eval "var minYear='2016/01/01/E-05452050';" checkAccessionDir.js

   Structure:
       {collection: {year: {month: {day: [DicomFilePath count, StudyDate count]}}}

   Log:
       2020-02-20 - BP - Create initial script
*/
const DB_NAME = "dicom";
const CONN = new Mongo();
CONN.getDB("").auth("", "");  // enter authorisation details

var db = CONN.getDB(DB_NAME);
var counts = {};

var acc_path = (typeof path === "undefined") ? "2016/01/01/E-05452050" : path;

function check_path() {
    db.getCollectionNames().forEach(function(collName) {
        if(collName === "series") { return; }

        print("Checking path  " + acc_path + " in coll " + collName);
        var dbColl = db.getCollection(collName);

        dbColl.find({"header.DicomFilePath": {$regex: "^" + acc_path}}).forEach(function(doc) {
            print("Found path " + acc_path + " in coll " + collName);
            printjson(doc.header.DicomFilePath);
        });
    })
}

check_path();