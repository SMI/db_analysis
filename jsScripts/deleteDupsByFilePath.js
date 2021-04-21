
const DB_NAME = "dicom";
const CONN = new Mongo();

// TODO: The username/password needs to be passed in here from the CLI
CONN.getDB("admin").auth("", "");

DB = conn.getDB(DB_NAME);

//TODO Need to loop over each image_* collection
coll = ...
coll.aggregate(
[
  { "$group":
    {
      "_id": {"fPath": "$header.DicomFilePath"},
      "duplicates": {"$push": "$_id"},
      "count": {"$sum": 1}
    }
  },
  { 
    "$match": {"count": {"$gt": 1}}
  },
  {
    // Limit for now, even though it has to group over everything
    "$limit": 10
  }
], 
{
  allowDiskUse: true
})
.forEach(function(doc) {
  
  //TODO: Perform the deletion here
  print("\nFile path: " + doc["fPath"]);
  doc.duplicates.forEach(function(id) {
    print("_id: " + id);
  });
});
