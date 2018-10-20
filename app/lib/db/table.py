class Table:

    def __init__(self, cursor):
        assert(cursor is not None)
        self._cursor = cursor

    def initialize(self):
        raise NotImplementedError()

    def destroy(self):
        raise NotImplementedError()


