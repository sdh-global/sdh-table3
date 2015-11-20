from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.template import RequestContext
from django.template.loader import  select_template, render_to_string

from ..plugin import BasePlugin


@python_2_unicode_compatible
class _RenderContext(object):
    def __init__(self, plugin, table_obj, table_cls):
        self.plugin = plugin
        self.table_obj = table_obj
        self.table_cls = table_cls

    def __str__(self):
        """
        Render table to string
        """
        template = self.plugin.get_template('main.html')

        ctx = RequestContext(self.table_obj.request)
        ctx['table'] = self.table_obj
        ctx['header'] = self.header()
        ctx['columns'] = self.columns()
        return template.render(ctx)

    def context(self):
        ctx = RequestContext(self.table_obj.request)
        ctx['table'] = self.table_obj
        ctx['header'] = self.header()
        ctx['columns'] = self.columns()
        return ctx

    def columns(self):
        for column_name in self.table_obj.columns:
            column = self.table_obj.base_columns[column_name]
            sort_mode = self.table_obj.features.get('sort',
                                               {}).get(column_name, None)

            if column.header_style and callable(column.header_style):
                style = column.header_style(self.table_obj)
            else:
                style = column.header_style

            yield {'table': self.table_obj,
                   'column_name': column_name,
                   'sort_mode': sort_mode,
                   'column': column,
                   'attrs': column.header_html_attrs(self.table_obj),
                   'style': style}

    def header(self):
        for column_data in self.columns():
            ctx = RequestContext(self.table_obj.request)
            ctx.update(column_data)
            template = self.plugin.get_template(column_data['column'].header_template)
            yield template.render(ctx)


class DjangoTemplatePlugin(BasePlugin):
    """Django template pluging
    Support rendering output content via Django tempalte

    Lookup request vairables:
        template: name of template for render output

    """
    output = 'html'
    base_path = 'ua2/table3/'

    def __init__(self, template_path=None):
        self.template_path = template_path or self.base_path

    def get_template(self, template_name):
        return select_template((self.template_path + template_name,
                                self.base_path + template_name))

    def render(self, table_obj, table_cls):
        return _RenderContext(self, table_obj, table_cls)
