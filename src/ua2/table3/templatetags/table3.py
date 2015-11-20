from django import template

register = template.Library()

# http://stackoverflow.com/questions/5755150/altering-one-query-parameter-in-a-url-django
@register.simple_tag(takes_context=True)
def url_replace(context, field, *args):
    dict_ = context['request'].GET.copy()
    dict_[field] = ''.join(args)
    return dict_.urlencode()

@register.simple_tag(takes_context=True)
def table_feature(context, table, *args):
    key = '_'.join(args)
    context['feature'] = table.features.get(key)
    return ''
