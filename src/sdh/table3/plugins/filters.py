from sdh.table3.plugin import BasePlugin


class CategoryFilter(BasePlugin):
    def __init__(self, categories, default=None):
        self.categories = categories
        self.default = default

    def process_request(self, table, request):
        table.features['category'] = {'options': self.categories,
                                      'selected': None}
        if request.method == 'GET':
            category = request.GET.get('category', self.default)
        else:
            category = request.POST.get('category', self.default)
        categories = dict(self.categories)
        if category in categories:
            table.features['category']['selected'] = category
            cb = getattr(table, 'category_filter', None)
            if cb and callable(cb):
                cb(category)


class DropdownFilter(BasePlugin):
    SLUG = 'dropdown'

    def __init__(self, key, options=None, label=None, default=None):
        """
        key - drop down filter parameter
        label = item Label
        options - list of 2 elements value + label
        """
        self.key = key
        self.label = label
        self._options = options
        self.default = default
        self.selected = None

    def options(self):
        cb = getattr(self.table, f'{self.SLUG}_options_{self.key}', None)
        if cb:
            self._options = cb(self, self._options)
        return self._options

    def process_request(self, table, request):
        if request.method == 'GET':
            self.selected = request.GET.get(self.key, self.default)
        else:
            self.selected = request.POST.get(self.key, self.default)

        state = {'options': self.options,
                 'key': self.key,
                 'label': self.label,
                 'selected': self.selected}

        plugins = table.features.get(self.SLUG, [])
        plugins.append(state)
        table.features[self.SLUG] = plugins
        table.features[f'{self.SLUG}_{self.key}'] = self

        if self.selected:
            cb = getattr(table, f'{self.SLUG}_filter_{self.key}', None)
            if cb and callable(cb):
                cb(self.selected)


class FilterFormPlugin(BasePlugin):
    SLUG = 'filter_form'

    def __init__(self, form):
        self.form = form

    def process_request(self, table, request):
        filter_form = self.form(request.GET or None, request=request)

        has_filters = filter_form.has_changed()

        form = {"body": filter_form, "buttons": {"apply": True, "back": True}}

        table.features[self.SLUG] = {'form': form, 'has_filters': has_filters}

        cb = getattr(table, self.SLUG, None)
        if cb and callable(cb):
            cb(filter_form)
