'''
Module for MongoDB.
'''

import os

from pymongo import MongoClient

mongo_client = MongoClient(os.getenv('MONGO_URI'))
mongo_db = mongo_client[os.getenv('MONGO_DB')]  # dev/prd


def get_mongo():
    ''' Global variable for MongoDB instance. '''
    return mongo_db
