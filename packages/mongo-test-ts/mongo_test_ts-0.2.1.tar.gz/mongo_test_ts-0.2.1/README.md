# MongoDB Connection Utility
## Overview

This Python package provides utility functions to simplify interactions with MongoDB databases. It allows you to easily create a MongoDB client, database, and collection, as well as insert records into the database.
Installation

#### You can install the package using pip:

bash

* pip install mongo_connection_owais

## Usage

#### To use this package, follow these steps:

   Import the mongo_operation class from the package:

* from mongo_connection_owais import mongo_operation

Create an instance of the mongo_operation class by providing the MongoDB connection URL, database name, and optional collection name:


* client_url = "mongodb://localhost:27017/"
* database_name = "my_database"
* collection_name = "my_collection"
* mongo_op = mongo_operation(client_url, database_name, collection_name)

#### Insert records into the MongoDB collection:

* record = {"key": "value"}
* mongo_op.insert_record(record, collection_name)

#### Perform bulk insertion of data from a CSV or Excel file:


* datafile = "data.csv"
* mongo_op.bulk_insert(datafile, collection_name)
