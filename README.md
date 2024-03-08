# Toycommons library
This is made to work as a general plug-in module for willdrug/toychest but can be adapted.

1. If ran via ToyInfra expects a MongoDB connection. This is mainly for configuration storage purposes. 
MongoDB is used as a config storage, command storage and cache.
2. Storage module proxies mongodb functions into actionable classes
3. Model module is mainly dataclasses to unify db work between apps
4. Drive module implements a connection to Google Drive, allowing to get and process drive files and Google Docs

# ToDo
1. Abstract out the whole module so it can be used without db connections and drive functionality is accessible directly
2. 

# Useful features
## MongoDB
Working with databases is boring.
### NameValue
This just gets stuff from collection based on "name" field and returns the "value" field. 
Made like this because it works.
### CachedDataclass
This gets stuff from collection as a NameValue and does not access the DB until a re-cache timer has passed.

### MessageDataClass
This provides an inbox with send and receive methods for objects subclassing Message 
It always uses domain+recipient and has only one command per recipient present;

## Google Drive
To use the drive module separately, initialize Config to have "drive_token", "drive_folder_id" 
and "drive_config_sync_ttl".

This will get you access to SyncedFile and function to parse Google Docs

### SyncedFile
File from Google Drive which is accessed via memory or local filesystem and synced on a timer or on command.

### Google Doc
from drive.google_doc_data import GoogleDocData

This class is a parser for Google Docs, turning Google json structure into unrollable recursive class. 
Implemented functions allows to transform Google Doc into other formats and back.

I might remove this code into a standalone script for general usage if anyone needs that.

# To Do
1. Add normal testing
2. Add obvious error auto checking (like failed imports)