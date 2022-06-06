'''
Module for MongoDB.
'''

import os

from fastapi import Request
from pymongo import MongoClient

mongo_client = MongoClient(os.getenv('MONGO_URI'))
mongo_db = mongo_client[os.getenv('MONGO_DB')]  # dev/prd


async def get_mongo(request: Request):
    ''' Global variable for MongoDB instance. '''
    return request.app.state.mongo_db
