"""
Querying user information.
"""

from pymongo.errors import PyMongoError

from app.services.mongo_service import get_mongo


def get_name(mail, database=get_mongo()):
    """
    Return a corresponding user name.
    """
    try:
        user = database.user.find_one({'mail': mail})
        return user['name']
    except (TypeError, PyMongoError):
        return None
