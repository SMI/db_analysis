/* MongoDB script that extracts one image matching given collection and date from MongoDB. 

   To run:
       For default collection (MR) and path date (2016/02/16):
           mongo getImage.js > image.txt

       For custom collection and path date:
           mongo --eval "var collection='image_CT'; var pathDate='2017/02/16'" getImage.js > image.txt

   Log:
       2020-01-30 - BP - Create initial script with input collection and path date
*/
const DB_NAME = "dicom";
const CONN = new Mongo();
CONN.getDB("").auth("", "");  // enter authorisation details

var db = CONN.getDB(DB_NAME);

function getImage() {
    var collection = (typeof coll === "undefined") ? "image_MR" : coll;
    var pathDate = (typeof date === "undefined") ? "2016/02/16" : date;

    var dbColl = db.getCollection(collection);

    print("Extracting image from collection " + collection + " for date " + pathDate);

    var image = dbColl.findOne({"header.DicomFilePath": {$regex: "^" + pathDate}});

    if (image) {
        printjson(image)
    } else {
        print("Sorry, image not found. Try another date or collection.")
    }
}

getImage();