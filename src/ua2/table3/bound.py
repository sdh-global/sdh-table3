class BoundCell(object):
    def __init__(self, column_name, table, row_number, data, row):
        self.column_name = column_name
        self.table = table
        self.column = table.base_columns[column_name]
        self.row_number = row_number
        self.data = data
        self.row = row
        self._cell_atts = None
        self._value = None

    def __unicode__(self):
        return unicode(self.value)

    @property
    def value(self):
        if self._value is None:
            self._value = self.column.get_value(self.table, self.row, row_number=self.row_number)
        return self._value

    def as_html(self):
        return self.column.as_html(self.table, self.row, row_number=self.row_number)

    @property
    def html_attrs(self):
        value = self.value
        if self._cell_atts is None:
            self._cell_atts = self.column.cell_html_attrs(
                self.table,
                self.row,
                value,
                row_number=self.row_number)
        return self._cell_atts


class BoundRow(object):
    def __init__(self, table, row_number, data, row):
        self.table = table
        self.number = row_number
        self.data = data
        self.row = row
        self.row_number = row_number

    @property
    def html_class(self):
        handler = self.table.get_handler('row_html_class')
        if handler:
            return handler(self.row,
                           row_number=self.row_number)

        return ''

    @property
    def html_attrs(self):
        handler = self.table.get_handler('row_html_attrs')
        if handler:
            return handler(self.row,
                           row_number=self.row_number)
        return ''

    def cells(self):
        for column_name in self.table.columns:
            yield BoundCell(column_name,
                            self.table,
                            self.row_number,
                            self.data,
                            self.row)
