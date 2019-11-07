// Counts the number of images per month in the "dicom" collection

const DB_NAME = "dicom";
const CONN = new Mongo();

// TODO: The username/password needs to be passed in here from the CLI
CONN.getDB("admin").auth("", "");

const KEY = "StudyDate"; // NOTE: This is indexed on all image_* collections
const YEARS = ["2015", "2016", "2017"];
const MONTHS = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
const COUNTS = {};

YEARS.forEach(function(year) {
  COUNTS[year] = {};
  MONTHS.forEach(function(month) {
    COUNTS[year][month] = 0;
  });
});

var DB = CONN.getDB(DB_NAME);
DB.getCollectionNames().forEach(function(collName) {
  if(collName === "series") {
    return;
  }  
  coll = DB.getCollection(collName);

  YEARS.forEach(function(year) {
    MONTHS.forEach(function(month) {
      // NOTE: The "^" at the start of the Regex it *very* important, as the index won't be used if it's missing
      COUNTS[year][month] += count = coll.count({"StudyDate": {$regex: "^" + year + month}});
    });
  });
});

// TODO: Pretty-print
print("\n--- Results ---\n");
printjson(COUNTS);
