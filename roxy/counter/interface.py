class AbstractCounter(object):
    """Абстрактный класс счетчика запросов"""

    def increment_by_key(self, key, value=1):
        """Увеличение кол-ва запросов по ключю"""
        raise NotImplementedError()

    def add_key(self, key, init_value=0):
        """Добавление нового ключа"""
        raise NotImplementedError()

    def get_count(self, key):
        """Получить текущее значение лимитов по ключю"""
        raise NotImplementedError()
