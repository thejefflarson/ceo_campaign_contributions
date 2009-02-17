from django import template

register = template.Library()
@register.simple_tag
def percent(part, whole):
    try:
        return int(round(float(part)/float(whole) * 100))
    except ZeroDivisionError:
        return 0

@register.inclusion_tag('finance/split_bar.html')
def splitbar(dict, total):
    return {'split': dict, 'total': total}

@register.inclusion_tag('finance/ceo_generic.html')
def ceo_generic(ceo):
    return {'ceo': ceo}

@register.inclusion_tag('finance/ceo_map.js')
def map_ceos(ceos):
    return {'ceo_list': ceos}
