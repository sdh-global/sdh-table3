from django.template import loader

from ..plugin import BasePlugin


class TemplateHeaderPlugin(BasePlugin):
    def __init__(self, template):
        self.template = template

    def process_request(self, table, request):
        html = loader.render_to_string(self.template, table.features.get('templateheader'), request=request)
        table.features['templateheader'] = {'html': html}
