from django import template
import settings

register = template.Library()
@register.simple_tag
def percent(part, whole):
    try:
        return int(round(float(part)/float(whole) * 100))
    except ZeroDivisionError:
        return 0

@register.inclusion_tag('finance/split_bar.html')
def splitbar(dict, total):
    if hasattr(dict, 'default_factory'): # just to be sure
        setattr(dict, 'default_factory', None)
    return {'split': dict, 'total': total}

@register.inclusion_tag('finance/ceo_generic.html')
def ceo_generic(ceo):
    return {'ceo': ceo}

@register.inclusion_tag('finance/ceo_map.js')
def map_ceos(ceos):
    return {'ceo_list': ceos, 'MEDIA_URL': settings.MEDIA_URL}
