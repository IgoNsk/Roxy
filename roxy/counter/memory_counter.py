from roxy.counter.interface import AbstractCounter


class MemoryCounter(AbstractCounter):

    _counters = {}

    def increment_by_key(self, key, value=1):
        self._counters[key] += value
        return self

    def get_count(self, key):
        return self._counters[key]

    def add_key(self, key, init_value=0):
        self._counters[key] = init_value
