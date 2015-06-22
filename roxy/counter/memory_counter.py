from roxy.counter.interface import Counter


class MemoryCounter(Counter):

    _counters = {}

    def add_key(self, key, init_value=0):
        self._counters[key] = init_value
        return self

    def increment_by_key(self, key, value=1):
        self._counters[key] += value
        return self

    def get_count(self, key):
        return self._counters[key]

    def clear_all(self):
        for key in self._counters:
            self._counters[key] = 0
        super().clear_all()