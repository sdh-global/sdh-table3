
class DjnagoORM(object):
    def __init__(self, qs=None):
        self.table = None
        self.request = None
        self.qs = qs

    def __call__(self, table, request):
        self.table = table
        self.request = request
        return self

    def __iter__(self):
        for item in self.qs:
            yield item
