import datetime

from django.db.models.manager import Manager
from django.utils.safestring import mark_safe
from django.urls import reverse, NoReverseMatch
from django.utils.html import escape
from django.template import loader, RequestContext, Template
from django.utils.formats import number_format, date_format
from django.forms.utils import flatatt

from django.utils import timezone


class Column(object):
    header_template = 'header_column.html'
    creation_counter = 0

    def __init__(self, label, refname=None, sortable=False, order_by=None,
                 header_style=None, header_attrs=None,
                 cell_attrs=None, default_value='',
                 **attrs):
        self.name = None  # fills by table metaclass
        self.label = label
        self.refname = refname
        self.sortable = sortable
        self.order_by = order_by
        self.header_style = header_style
        self.header_attrs = header_attrs or {}
        self._cell_attrs = cell_attrs or {}
        self.extra_cell_attrs = {}
        self.attrs = attrs
        self.default_value = default_value
        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1

    def __str__(self):
        return self.column.label

    def _recursive_value(self, row, keylist):
        value = None
        if hasattr(row, keylist[0]):
            value = getattr(row, keylist[0])
            if callable(value):
                if value.__class__.__name__ == 'ManyRelatedManager':
                    value = value.all()
                else:
                    value = value()
            if len(keylist) > 1:
                return self._recursive_value(value, keylist[1:])
        return value

    def get_value(self, table, row, refname=None, default=None, **kwargs):
        handler = table.get_handler('value_%s' % self.name)
        if handler:
            return handler(row, **kwargs)

        value = self._recursive_value(
            row,
            (refname or self.refname or self.name).split('__'))

        if value is not None:
            if isinstance(value, Manager):
                return value.all()
            return value
        return default

    def as_html(self, table, row, **kwargs):
        handler = table.get_handler('render_html_%s' % self.name)
        if handler:
            return handler(row, **kwargs)

        value = self.get_value(table, row, **kwargs)
        if value is None:
            return self.default_value
        return value

    def header_html_attrs(self, table):
        return flatatt(self.header_attrs)

    def cell_html_attrs(self, table, row, value, row_number):
        """ render html cell attr """
        result_attrs = {}

        if callable(self._cell_attrs):
            result_attrs.update(self._cell_attrs(table, row, value, row_number))
        elif isinstance(self._cell_attrs, dict):
            result_attrs.update(self._cell_attrs)

        result_attrs.update(self.extra_cell_attrs)
        return flatatt(result_attrs)


class LabelColumn(Column):
    pass


class DateTimeColumn(Column):
    def __init__(self, *args, **attrs):
        self.format = attrs.pop('format', None)
        self.localize = attrs.pop('localize', True)
        super(DateTimeColumn, self).__init__(*args, **attrs)

    def as_html(self, table, row, **kwargs):
        value = self.get_value(table, row, **kwargs)
        if value is None:
            return self.default_value

        if self.localize and isinstance(value, datetime.datetime) and timezone.is_aware(value):
            value = timezone.make_naive(value)

        if isinstance(value, datetime.datetime) and not self.format:
            _format = 'DATETIME_FORMAT'
        elif isinstance(value, datetime.date) and not self.format:
            _format = 'DATE_FORMAT'
        else:
            _format = self.format

        return date_format(value, _format)


class DateColumn(DateTimeColumn):
    def __init__(self, *args, **attrs):
        _format = attrs.pop('format', 'DATE_FORMAT')
        super().__init__(*args, format=_format, **attrs)


class HrefColumn(Column):
    def __init__(self, *args, **attrs):
        self.reverse = attrs.pop('reverse', None)
        self.reverse_args = attrs.pop('reverse_args', [])
        self.get_args = attrs.pop('get', '')
        super(HrefColumn, self).__init__(*args, **attrs)

    def resolve(self, table, row):
        if callable(self.reverse):
            return self.reverse(row)

        if not self.reverse:
            return ''

        reverse_args = self.reverse_args
        if callable(reverse_args):
            reverse_args = reverse_args(row)
        elif isinstance(self.reverse_args, (list, tuple)):
            reverse_args = [self.get_value(table, row, refname=item) for item in reverse_args]
        elif isinstance(reverse_args, str):
            reverse_args = [self.get_value(table, row, refname=reverse_args)]

        try:
            href = reverse(self.reverse, args=reverse_args)
        except NoReverseMatch:
            href = "#NoReverseMatch"
        return href

    def as_html(self, table, row, **kwargs):
        value = self.get_value(table, row)
        if value is None:
            return self.default_value

        url = self.resolve(table, row)
        if url is None:
            return super().as_html(table, row, **kwargs)

        html = "<a href='{href}{get_args}' {attrs}>{content}</a>".format(
            href=self.resolve(table, row),
            attrs=flatatt(self.attrs),
            content=escape(self.get_value(table, row)),
            get_args=self.get_args)
        return mark_safe(html)


class TemplateColumn(Column):
    def __init__(self, *args, **attrs):
        self.template = attrs.pop('template', None)
        super(TemplateColumn, self).__init__(*args, **attrs)

    def as_html(self, table, row, **kwargs):
        if not self.template:
            return ''

        return loader.render_to_string(
            self.template,
            {'table': table,
             'record': row,  # for compatibility with django_tables2 tempaltes
             'row': row},
            request=table.request)


class InlineTemplateColumn(Column):
    def __init__(self, *args, **attrs):
        self.template = Template(attrs.pop('template', None))
        super(InlineTemplateColumn, self).__init__(*args, **attrs)

    def as_html(self, table, row, **kwargs):
        return self.template.render(
            RequestContext(table.request,
                           {'table': table,
                            'record': row,  # for compatibility with django_tables2 tempaltes
                            'row': row}))


class CheckboxColumn(Column):
    header_template = 'header_checkbox.html'

    def __init__(self, label=None, **attrs):
        super(CheckboxColumn, self).__init__(label, **attrs)

    def as_html(self, table, row, **kwargs):
        attrs = self.attrs.copy()
        attrs['type'] = 'checkbox'
        attrs['autocomplete'] = 'off'
        attrs['name'] = escape(self.name)
        attrs['value'] = escape(self.get_value(table, row, **kwargs))

        html = "<input {attrs} />".format(attrs=flatatt(attrs))
        return mark_safe(html)


class MoneyColumn(Column):
    def __init__(self, label=None, refname=None, cell_class='money', positive_format='%s', negative_format='-%s', decimal_pos=2, force_grouping=True,
                 empty_value='', *args, **attrs):
        super(MoneyColumn, self).__init__(label, refname, *args, **attrs)
        self.positive_format = positive_format
        self.negative_format = negative_format
        self.decimal_pos = decimal_pos
        self.force_grouping = force_grouping
        self.empty_value = empty_value
        self.extra_cell_attrs['class'] = cell_class

    def as_html(self, table, row, **kwargs):
        value = self.get_value(table, row, **kwargs)
        if value is not None:
            if value < 0:
                format_string = self.negative_format
            else:
                format_string = self.positive_format

            return format_string % number_format(
                abs(value), use_l10n=True, decimal_pos=self.decimal_pos,
                force_grouping=True)

        return self.empty_value
