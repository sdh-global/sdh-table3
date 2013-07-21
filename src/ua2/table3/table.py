from ua2.table3.plugin import BasePlugin, StopProcessing
from ua2.table3.column import Column
from collections import OrderedDict

class RowsIterator(object):
    def __init__(self, table, data):
        self.table = table
        self.data = data

    def __iter__(self):
        for row in self.data:
            yield row


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
    def __new__(cls, name, bases, attrs):
        attrs['base_columns'] = get_declared_columns(bases, attrs)

        new_class = super(TableBaseMetaclass,
                     cls).__new__(cls, name, bases, attrs)


class Table(object):
    __metaclass__ = TableBaseMetaclass

    def __init__(self):
        self.request_proxy = None # Class handler incoming request and convert it into internal Request class
        self.data_proxy = None # Class that retrieve data from extetnal storage

        self.plugins = []

        self.plugins_request = []
        self.plugins_output = {}

    def load_plugins(self, plugins):
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

            output = getattr(plugin, 'output')
            if output and hasattr(plugin, 'process_output'):
                if output in self.plugins_output:
                    raise ValueError('Output process %s already registered' % output)
                self.plugins_output[output] = plugin.process_output


    def handler_request(self, _request):
        request = self.request_proxy(_request)

        for handler in self.plugins_request:
            try:
                handler(request)
            except StopProcessing, e:
                return request.response(e)

        output_handler = self.plugins_output[request.output]

        data = self.data_proxy(self, request)
        return request.build_response(self, output_handler, data)

    def iter_rows(self, request, data):
        return RowsIterator(self, data)
