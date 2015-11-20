from ua2.table3.plugin import BasePlugin


class CategoryFilter(BasePlugin):
    def __init__(self, categories, default=None):
        self.categories = categories
        self.default = default

    def process_request(self, table, request):
        table.features['category'] = {'options': self.categories,
                                      'selected': None}

        category = request.REQUEST.get('category', self.default)
        categories = dict(self.categories)
        if category in categories:
            table.features['category']['selected'] = category
            cb = getattr(table, 'category_filter', None)
            if cb and callable(cb):
                cb(category)


class DropdownFilter(BasePlugin):
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
        cb = getattr(self.table, 'dropdown_options_%s' % self.key, None)
        if cb:
            self._options = cb(self, self._options)
        return self._options

    def process_request(self, table, request):
        self.selected = request.REQUEST.get(self.key,
                                            self.default)

        state = {'options': self.options,
                 'key': self.key,
                 'label': self.label,
                 'selected': self.selected}

        plugins = table.features.get('dropdown', [])
        plugins.append(state)
        table.features['dropdown'] = plugins
        feature_key = 'dropdown_%s' % self.key
        table.features[feature_key] = self

        if self.selected:
            cb = getattr(table, 'dropdown_filter_%s' % self.key, None)
            if cb and callable(cb):
                cb(self.selected)
