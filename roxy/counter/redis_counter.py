from roxy.counter.interface import AbstractCounter


class RedisCounter(AbstractCounter):

    def __init__(self, redis_client):
        self.redis_client = redis_client.to_blocking_client()

    def increment_by_key(self, key, value=1):
        self.redis_client.incr(key, value)
        return self

    def get_count(self, key):
        val = self.redis_client.get(key)
        if val is None:
            raise KeyError()

        return int(val)

    def add_key(self, key, init_value=0):
        self.redis_client.set(key, init_value)
