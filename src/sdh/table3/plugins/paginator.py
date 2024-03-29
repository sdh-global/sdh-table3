import math

from ..plugin import BasePlugin
from ..settings import (CFG_TABLE_ROW_PER_PAGE, CFG_TABLE_PAGINATOR,
                        CFG_TABLE_PAGE_PER_SEGMENT)


class Paginator(object):
    def __init__(self, table, request, row_per_page):
        self.table = table
        self.request = request

        try:
            if request.method == 'GET':
                self.row_per_page = int(request.GET.get('row_per_page', row_per_page))
            else:
                self.row_per_page = int(request.POST.get('row_per_page', row_per_page))
        except ValueError:
            self.row_per_page = row_per_page

        try:
            if request.method == 'GET':
                page_number = request.GET.get('page', 1)
            else:
                page_number = request.POST.get('page', 1)
            self.page_number = max(int(page_number), 1)
        except ValueError:
            self.page_number = 1

        self.page_per_segment = CFG_TABLE_PAGE_PER_SEGMENT

        # internal cache
        self._data_length = None
        self._pages_count = None
        self._bar = None
        self._url_prefix = None

        self.table.rows_iterator = self.rows_iterator

        if self.page_number > self.pages_count:
            self.page_number = self.pages_count

    @property
    def rows_iterator(self):
        start, end = self.range
        if hasattr(self.table.data, 'clone'):
            return self.table.data.clone()[start:end]
        return self.table.data[start:end]

    @property
    def data_length(self):
        """ Return input data length (in rows)
        """
        if self._data_length is None:
            if isinstance(self.table.data, (list, tuple)):
                self._data_length = len(self.table.data)
            else:
                self._data_length = self.table.data.count()
        return self._data_length

    @property
    def pages_count(self):
        if self._pages_count is None:
            self._pages_count = int(math.ceil(
                    float(self.data_length) / float(self.row_per_page)))
            if not self._pages_count:
                self._pages_count = 1
        return self._pages_count

    @property
    def range(self):
        start = (self.page_number - 1) * self.row_per_page
        end = self.page_number * self.row_per_page
        return start, end

    @property
    def page_bar(self):
        """ return page numbers """
        if self._bar is None:
            self._bar = []
            for page in range(self.page_number - self.page_per_segment // 2,
                              self.page_number + self.page_per_segment // 2 + 1):
                if page <= 0 or page > self.pages_count:
                    continue

                self._bar.append(page)
        return self._bar

    @property
    def prev_page_number(self):
        if self.page_number - 1 <= 0:
            return None

        return self.page_number - 1

    @property
    def next_page_number(self):
        if self.page_number + 1 > self.pages_count:
            return None
        return self.page_number + 1

    @property
    def prev_page_segment(self):
        if self.page_number - self.page_per_segment // 2 - 1 <= 1:
            return None

        return (self.page_number - self.page_per_segment // 2 - 1) or 1

    @property
    def next_page_segment(self):
        if self.page_number + self.page_per_segment // 2 + 1 >= self.pages_count:
            return None

        return self.page_number + self.page_per_segment // 2 + 1

    @property
    def show_first_page(self):
        return 1 not in self.page_bar

    @property
    def show_last_page(self):
        return self.pages_count not in self.page_bar

    @property
    def url_args_prefix(self):
        if self._url_prefix is not None:
            return self._url_prefix

        if not hasattr(self.request, 'GET'):
            self._url_prefix = '?'
            return self._url_prefix

        self._url_prefix = '?'

        qset = self.request.GET.copy()
        if 'page' in qset:
            del qset['page']

        if len(qset) > 0:
            self._url_prefix += qset.urlencode()
            self._url_prefix += '&'

        return self._url_prefix

    def is_paginate(self):
        return self.pages_count > 1


class PaginatorPlugin(BasePlugin):
    def __init__(self, row_per_page=None, paginator_cls=None):
        self.row_per_page = row_per_page or CFG_TABLE_ROW_PER_PAGE
        self.paginator_cls = paginator_cls or CFG_TABLE_PAGINATOR or Paginator

    def process_request(self, table, request):
        page = request.GET.get('page') if request.method == 'GET' else request.POST.get('page')
        if page != 'all':
            table.features['paginator'] = self.paginator_cls(table,
                                                             request,
                                                             self.row_per_page)


class LazyPaginator(Paginator):

    def __init__(self, *args, **kwargs):
        self._rows = None
        self._more = False
        super().__init__(*args, **kwargs)

    def get_rows(self):
        data = self.table.data
        if hasattr(data, 'clone'):
            data = data.clone()
        start, end = self.range
        rows = list(data[start:end + 1])
        more = len(rows) > self.row_per_page
        if more:
            rows = rows[:self.row_per_page]
        return rows, more

    @property
    def rows_iterator(self):
        if self._rows is None:
            self._rows, self._more = self.get_rows()
            if not self._rows and self.page_number > 1:
                self._rows, self._more = self.get_rows()
        return self._rows

    @property
    def pages_count(self):
        if self._more:
            return self.page_number + 1
        else:
            return self.page_number

    @property
    def next_page_number(self):
        if self._more:
            return self.page_number + 1
