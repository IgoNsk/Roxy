import tornado.ioloop


class Counter(object):
    def __init__(self):
        super(Counter, self).__init__()

    def clear_all(self):
        print('Clear of counters')

    def initialization(self):
        task = tornado.ioloop.PeriodicCallback(
            self.clear_all,
            60 * 1000)
        task.start()