from sdh.table3.plugin import BasePlugin


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
    def __init__(self, default_order_by=None):
        self.default_order_by = default_order_by

    def set_ordering_mode(self, order_by, mode):
        prefix = ''
        if mode == 'desc':
            prefix = '-'

        return ['%s%s' % (prefix, item) for item in order_by]

    def process_request(self, table, request):
        table.features['sort'] = {}
        sort_by = request.GET.get('sort_by') if request.method == 'GET' else request.POST.get('sort_by')
        sort_by = sort_by or self.default_order_by
        if not sort_by:
            return

        if sort_by[0] == '-':
            sort_mode = 'desc'
            sort_by = sort_by[1:]
        else:
            sort_mode = 'asc'

        for column_name in table.columns:
            if column_name == sort_by:
                table.features['sort'][column_name] = sort_mode
                column = table.base_columns[column_name]
                order_by = []
                if column.order_by:
                    order_by += column.order_by
                else:
                    order_by.append(column.refname)

                order_by = self.set_ordering_mode(order_by, sort_mode)
                table.data = table.data.order_by(*order_by)
