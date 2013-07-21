from django.http import HttpResponse


class BaseRequest(object):
    source = 'HTTP' # HTTP, AJAX, CELERY, WAMP, ...
    method = 'GET' # GET, POST, PUT, ...
    args = {}
    output = 'html' #html, json, csv, ...

    def get(self, key, default=None):
        return self.args.get(key, default)


class DjangoRequest(BaseRequest):
    def __init__(self, request):
        self.source = 'HTTP'
        self.request = request
        if request.is_ajax():
            self.source = 'AJAX'
        self.args = request.REQUEST
        self.output = self.args.get('output', self.output)

    def __getattr__(self, name):
        return getattr(self.request, name)

    def build_response(self, table, output_handler, data):
        mimetype = getattr(output_handler, 'mimetype', 'text/html')

        return HttpResponse(output_handler(self, table, data),
                            mimetype=mimetype)
