import logging
import os

import redis


class Singleton:
    __instance = None

    @classmethod
    def __get_instance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__get_instance
        return cls.__instance


class MyRedis(Singleton):
    def __init__(self):
        try:
            redis_host: str = os.getenv("REDIS_HOST")
            redis_port: int = int(os.getenv("REDIS_PORT"))  # might raise TypeError
            redis_db: int = int(os.getenv("REDIS_DB"))      # might raise TypeError
            redis_password: str = os.getenv("REDIS_PASSWORD")
            self.rds = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                socket_timeout=2,
                ssl=True,
            )
            logging.info("Redis connection succeeded.")
        except (redis.RedisError, TypeError) as error:
            logging.error("Redis connection failed. %s", error)


rds = MyRedis.instance().rds
