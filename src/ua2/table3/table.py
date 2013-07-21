from ua2.table3.plugin import BasePlugin, StopProcessing
from ua2.table3.column import Column, BaseColumnHeader
from collections import OrderedDict


def get_declared_columns(bases, attrs, with_base_fields=True):
    #inspired from django.forms.forms.get_declared_fields

    columns = [(column_name, attrs.pop(column_name))
               for column_name, obj in attrs.items() if isinstance(obj, Column)]
    columns.sort(key=lambda x: x[1].creation_counter)
    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, 'base_columns'):
                columns = base.base_columns.items() + columns
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_columns'):
                columns = base.declared_columns.items() + columns

    return OrderedDict(columns)


class TableBaseMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        attrs['base_columns'] = get_declared_columns(bases, attrs)

        new_class = super(TableBaseMetaclass,
                     mcs).__new__(mcs, name, bases, attrs)
        return new_class


class Table(object):
    __metaclass__ = TableBaseMetaclass

    """
    request.settings = all available settings to be modified by plugins
    Inside this instance plugins can't modify members
    """

    def __init__(self):
        self.request_proxy = None # Class handler incoming request and convert it into internal Request class
        self.data_proxy = None # Class that retrieve data from extetnal storage

        self.plugins = []

        self.plugins_request = []
        self.plugins_output = {}
        self.request = None
        self.column_header_cls = None

    def load_plugins(self, plugins):
        column_header_classes = [BaseColumnHeader]

        for item in plugins:
            if isinstance(item, BasePlugin):
                plugin = item
            elif issubclass(item, BasePlugin):
                plugin = item()
            else:
                raise ValueError("Plugin shoud be subclass of BasePluging")
            self.plugins.append(plugin)

            if hasattr(plugin, 'process_request'):
                self.plugins_request.append(plugin.process_request)

            if hasattr(plugin, 'column_header'):
                column_header_classes.append(plugin.column_header)

            output = getattr(plugin, 'output', None)
            if output and hasattr(plugin, 'process_output'):
                if output in self.plugins_output:
                    raise ValueError('Output process %s already registered' % output)
                self.plugins_output[output] = plugin.process_output

        self.column_header_cls = type('ColumnHeader',
                                      tuple(column_header_classes),
                                      {})


    def handler_request(self, _request):
        self.request = self.request_proxy(_request)
        self.request['columns'] = self.base_columns.keys()

        for handler in self.plugins_request:
            try:
                handler(self.request)
            except StopProcessing, e:
                return self.request.response(e)

        output_handler = self.plugins_output[self.request.output]

        data = self.data_proxy(self, self.request)
        return self.request.build_response(self, output_handler, data)

    def iter_rows(self, data):
        row_number = 1
        for row in data:
            yield BoundRow(self,
                           row_number,
                           self.request,
                           data,
                           row)
            row_number += 1


    def iter_headers(self):
        for key in self.request['columns']:
            yield self.column_header_cls(self.request, key, self.base_columns[key])


class BoundRow(object):
    def __init__(self, table, row_number, request, data_proxy, row):
        self.table = table
        self.row_number = row_number
        self.request = request
        self.data_proxy = data_proxy
        self.row = row


    def __unicode__(self):
        return unicode(self.row)

    def __iter__(self):
        for column_id in self.request['columns']:
            yield BoundCell(self.table,
                            self.row_number,
                            self.request,
                            self.data_proxy,
                            self.row,
                            column_id,
                            self.table.base_columns[column_id])
    @property
    def number(self):
        return self.row_number


class BoundCell(object):
    def __init__(self, table, row_number, request, data_proxy, row, id, column):
        self.table = table
        self.row_number = row_number
        self.request = request
        self.data_proxy = data_proxy
        self.row = row
        self.id = id
        self.column = column

    def __unicode__(self):
        return self.id

    def value(self):
        return self.data_proxy.resolve(self.row,
                                       self.id,
                                       self.column)
