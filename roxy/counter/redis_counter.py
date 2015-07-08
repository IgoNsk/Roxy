from roxy.counter.interface import AbstractCounter


class RedisCounter(AbstractCounter):
    """Класс хранения в REDIS значений счетчиков лимитов"""

    def __init__(self, redis_client):
        self.redis_client = redis_client.to_blocking_client()

    def __parse_val(self, val):
        """Преобразование возвращаемого значения из REDIS в число"""
        if val is None:
            raise KeyError()

        return int(val)

    def increment_by_key(self, key, value=1):
        val = self.redis_client.incr(key, value)
        return self.__parse_val(val)

    def get_count(self, key):
        val = self.redis_client.get(key)
        return self.__parse_val(val)

    def add_key(self, key, init_value=0):
        self.redis_client.set(key, init_value)
