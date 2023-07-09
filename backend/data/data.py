from pymongo import MongoClient

mongo_client: MongoClient = None


def init_client(cfg: dict):
    global mongo_client
    mongo_client = MongoClient(cfg['database']['host'], cfg['database']['port'])


def get_db(name):
    return mongo_client[name]
