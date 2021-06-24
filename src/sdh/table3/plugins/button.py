from django.template import loader

from ..plugin import BasePlugin


class TemplateButtonsPlugin(BasePlugin):
    def __init__(self, template):
        self.template = template

    def process_request(self, table, request):
        html = loader.render_to_string(self.template, {'table': table}, request=request)
        table.features['templatebuttons'] = {'html': html}
