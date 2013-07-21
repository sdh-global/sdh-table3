from ua2.table3.plugin import BasePlugin

class SortedColumnHeader(object):
    ASC = '*'
    DESC = '-'

    def sort_by(self, direction):
        sort_key = self.request['sort_by'] or ''
        return sort_key[1:] == self.id and sort_key[0] == direction

    def is_asc(self):
        return self.sort_by(self.ASC)

    def is_desc(self):
        return self.sort_by(self.DESC)


class SingleSortPlugin(BasePlugin):
    column_header = SortedColumnHeader

    def process_request(self, request):
        request['sort_by'] = request.get('sort_by')
