

class AbstractCounter(object):

    def increment_by_key(self, key, value=1):
        raise NotImplementedError()

    def add_key(self, key, init_value=0):
        raise NotImplementedError()

    def get_count(self, key):
        raise NotImplementedError()
