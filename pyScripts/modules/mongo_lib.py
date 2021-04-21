'''Library class that holds general database-related functionality
'''
import sys
import os
import pprint
import pymongo
from bson.code import Code


class DbLib:
    def __init__(self):
        self.client = None
        self.db = None

        self.connect()

    def connect(self):
        '''Connect to MongoDB database based on credentials available via
           env vars.
        '''
        try:
            self.client = pymongo.MongoClient(
                os.environ.get("HOST"),
                username=os.environ.get("USER"),
                password=os.environ.get("PASS"),
                authSource=os.environ.get("AUTHDB")
            )
            print("Successful connection")
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed connection: {error}")
            sys.exit(1)


    def switch_db(self, db_name):
        '''Connects to specified database.'''
        try:
            self.db = self.client[db_name]
            print(f"Successfully switched to {db_name}")
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed switching to {db_name}: {error}")
            sys.exit(1)


    def list_collections(self):
        '''Lists collections in current database.'''
        try:
            collections = sorted(list(self.db.list_collection_names()))
            print(f"Successfully extracted collections from current db")
            return collections
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed extracting collections from current db: {error}")
            return False


    def create_index(self, collection, index, uniq=False):
        '''Creates an index in a given collection.'''
        try:
            self.db[collection].create_index([(index, pymongo.ASCENDING)], unique=uniq)
            print(f"Successfully created an index for {index} in {collection}")
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed creating index {index} in {collection}: {error}")
            return False

        
    def list_indexes(self, collection):
        '''Lists indexes in a given collection.'''
        try:
            index_info = sorted(list(self.db[collection].index_information()))
            print(f"Successfully extracted indexes from {collection}")
            return index_info
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed extracting indexes from {collection}: {error}")
            return False


    def find_one(self, collection):
        '''Finds and returns one document in a given collection.'''
        try:
            doc = self.db[collection].find_one()
            print(f"Successfully found one document in collection {collection}")
            return doc
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed finding one document in collection {collection}: {error}")
            return False


    def sample(self, collection, number):
        '''Finds and returns a given number of sample documents in a
           given collection.
        '''
        query = [
            {"$sample": {"size": number}}
        ]

        try:
            samples = self.db[collection].aggregate(query)
            print(f"Successfully extracted {number} sample document(s) from collection {collection}")
            return list(samples)
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed extracting {number} sample documens from collection {collection}: {error}")
            return False


    def count_documents(self, collection):
        '''Returns a count of the documents in a given collection.'''
        try:
            count = self.db[collection].count_documents({})
            print(f"Successfully counted documents in {collection}")
            return count
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed counting documents in {collection}: {error}")
            return False

        
    def count_by_modality(self, collection, modality="all"):
        '''Returns a count of the documents in a given collection by modality.
           If a modality name is specified, only the count for that modality
           will be returned, else, counts for all modalities will be returned.
        '''
        if modality == "all":
            query = [
                {"$group": {"_id": "$Modality", "count": {"$sum": 1}}}
            ]
        else:
            query = [
                {"$match": {"Modality": modality}},
                {"$group": {"_id": modality, "count": {"$sum": 1}}}
            ]

        try:
            count = self.db[collection].aggregate(query)
            print(f"Successfully counted documents in {collection}")
            return list(count)
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed counting documents in {collection}: {error}")
            return False


    def count_images(self, collection):
        '''Returns a count of the images in a given collection by modality.
           For the "series" collection, the count is done by the ImagesInSeries
           tag and for other collections, this is just the count of documents.
        '''
        if collection == "series":
            query = [
                {"$group": {
                "_id": "$Modality",
                "avgImages": {"$avg": "$header.ImagesInSeries"},
                "count": {"$sum": "$header.ImagesInSeries"}
                }},
                {"$project": {
                "_id": "$_id",
                "avgImages": {"$floor": "$avgImages"},
                "totalImages": "$count"
                }}
            ]
        else:
            query = [
                {"$group": {"_id": "null", "count": {"$sum": 1}}}
            ]

        try:
            count = self.db[collection].aggregate(query, allowDiskUse=True)
            print(f"Successfully counted images in {collection}")
            return list(count)
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed counting images in {collection}: {error}")
            return False


    def count_by_regex(self, collection, field, regex):
        '''Returns a count of the documents that contain given field and
           value in field matches regex.
        '''
        query = [
            {"$match": {field: regex}},
            {"$group": {
                "_id": "null",
                "count": {"$sum": 1}
            }}
        ]

        try:
            count = self.db[collection].aggregate(query, allowDiskUse=True)
            print(f"Successfully counted images in {collection}")
            return list(count)
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed counting images in {collection}: {error}")
            return False


    def list_tags(self, collection):
        '''Returns a list of distinct tags in a given collection.'''
        map_query = Code("function() {"
                         "    for (var key in this) {"
                         "        emit(key, null);"
                         "    }"
                         "}"
        )

        reduce_query = Code("function(key, value) {"
                            "    return null;"
                            "}"
        )

        output = collection + "_keys"

        try:
            result = self.db[collection].map_reduce(map_query, reduce_query, out=output)
            print(f"Successfully retrieved a list of tags from collection {collection}")

            try:
                distinct = result.distinct("_id")
                print(f"Successfully retrieved a list of distinct tags from collection {collection}")
                return distinct
            except (Exception, pymongo.errors.PyMongoError) as error:
                print(f"Failed retrieving a list of distinct tags from {collection}: {error}")
                return False
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed retrieving a list of tags from {collection}: {error}")
            return False


    def list_unique_vals(self, collection, tag):
        '''Returns a list of distinct values for a given tag in a given collection
           and the number of documents with that value by year.
        '''
        query = [
            {"$group": {
                "_id": {
                    "year": {
                        "$substr": ["$StudyDate", 0, 4]
                    },
                    f"{tag}": f"${tag}"
                },
                "total": {"$sum": 1}
            }},
            {"$group": {
                "_id": "$_id.year",
                f"{tag}s": {
                    "$push": {
                        "term": f"$_id.{tag}",
                        "total": "$total"
                    }
                }
            }}
        ]

        try:
            count = self.db[collection].aggregate(query, allowDiskUse=True)
            print(f"Successfully extracted distinct list of {tag} from {collection}")
            return list(count)
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed extracting distinct list of {tag} from {collection}: {error}")
            return False


    def list_null_vals(self, collection, tag):
        '''Returns a list of distinct values for a given tag in a given collection
           and the number of documents with that value by year.
        '''
        query = [
            {"$group": {
                "_id": {
                    "year": {
                         "$substr": ["$StudyDate", 0, 4]
                    },
                    f"{tag}": {"$or": [
                        {"$eq": [f"${tag}", "null"]},
                        {"$gt": [f"${tag}", "null"]},
                    ]}
                },
                "total": {"$sum": 1}
            }}
        ]

        try:
            count = self.db[collection].aggregate(query, allowDiskUse=True)
            print(f"Successfully extracted distinct list of {tag} from {collection}")
            return list(count)
        except (Exception, pymongo.errors.PyMongoError) as error:
            print(f"Failed extracting distinct list of {tag} from {collection}: {error}")
            return False


    def disconnect(self):
        '''Disconnect from the database'''
        if self.client is not None:
            self.client.close()
            print("Successful disconnection")