# coding: UTF-8
from datetime import datetime


class IntervalCounterHandler:

    PERIODS = {'minute', 'hour', 'day', 'month'}

    def __init__(self, period, prefix=None):
        if period not in self.PERIODS:
            raise NotImplementedError("Неизвестный интервал %" % period)

        self.period = period
        self.prefix = prefix

    def get_cur_key(self):
        parts = []
        if self.prefix:
            parts.append(self.prefix)

        date = datetime.utcnow()
        parts.extend([date.year, date.month])

        if self.period == 'day':
            parts.extend([date.day])
        elif self.period == 'hour':
            parts.extend([date.day, date.hour])
        elif self.period == 'minute':
            parts.extend([date.day, date.hour, date.minute])

        return '-'.join(map(lambda x: str(x), parts))