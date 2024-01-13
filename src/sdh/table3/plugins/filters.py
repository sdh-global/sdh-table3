from sdh.table3.plugin import BasePlugin


class BaseFilterPlugin(BasePlugin):
    SLUG = None

    def __init__(self, *args, filter_type=None, **kwargs):
        self.filter_type = filter_type

    @property
    def feature_key(self):
        return self.SLUG

    @property
    def parameter_key(self):
        return self.SLUG

    def extract_parameter(self, request, default):
        if request.method == 'POST':
            return request.POST.get(self.parameter_key, default)
        else:
            return request.GET.get(self.parameter_key, default)

    def set_feature(self, table, feature, value):
        table.features[self.feature_key][feature] = value

    def process_request(self, table, request):
        table.features[self.feature_key] = dict()
        if self.filter_type:
            name = 'category_%s.html' % self.filter_type
        else:
            name = None

        self.set_feature(table, 'template_name', name)


class CategoryFilter(BaseFilterPlugin):
    SLUG = 'category'

    def __init__(self, categories, default=None, **kwargs):
        self.categories = categories
        self.default = default
        super().__init__(**kwargs)

    def process_request(self, table, request):
        super(CategoryFilter, self).process_request(table, request)
        self.set_feature(table, 'options', self.categories)
        self.set_feature(table, 'selected', None)

        category = self.extract_parameter(request, self.default)

        categories = dict(self.categories)

        if category in categories:
            self.set_feature(table, 'selected', category)

            cb = getattr(table, 'category_filter', None)
            if cb and callable(cb):
                cb(category)


class DropdownFilter(BaseFilterPlugin):
    SLUG = 'dropdown'

    def __init__(self, key, options=None, label=None, default=None, **kwargs):
        """
        key - drop down filter parameter
        label = item Label
        options - list of 2 elements value + label
        """
        self.key = key
        self.label = label
        self._options = options
        self.default = default
        super().__init__(**kwargs)

    @property
    def feature_key(self):
        return f"{self.SLUG}_{self.key}"

    @property
    def parameter_key(self):
        return self.key

    def options(self):
        cb = getattr(self.table, f'{self.SLUG}_options_{self.key}', None)
        if cb:
            self._options = cb(self, self._options)
        return self._options

    def process_request(self, table, request):
        super().process_request(table, request)
        selected = self.extract_parameter(request, self.default)

        self.set_feature(table, 'options', self.options)
        self.set_feature(table, 'key', self.key)
        self.set_feature(table, 'label', self.label)
        self.set_feature(table, 'selected', selected)

        if selected:
            cb = getattr(table, f'{self.SLUG}_filter_{self.key}', None)
            if cb and callable(cb):
                cb(selected)


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
