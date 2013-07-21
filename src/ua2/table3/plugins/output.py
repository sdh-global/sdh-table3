from ua2.table3.plugin import BasePlugin
from django.template import loader, RequestContext


class DjangoTemplatePlugin(BasePlugin):
    """Django template pluging
    Support rendering output content via Django tempalte

    Lookup request vairables:
        template: name of template for render output

    """
    output = 'html'

    def __init__(self, template=None):
        self.template = template or 'ua2/table3/main.html'

    def process_request(self, request):
        self.template = request.get('template',
                                    self.template)

    def process_output(self, request, table, data):
        kwargs = {'table': table,
                  'rows': table.iter_rows(data),
                  'context_instance': RequestContext(request)}
        return loader.render_to_string(self.template,
                                       dictionary=kwargs,
                                       context_instance=RequestContext(request))
    process_output.mimetype = 'text/html'
