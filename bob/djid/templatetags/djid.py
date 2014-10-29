from django import template

from bob.djid import Djid


register = template.Library()


@register.inclusion_tag('djid.html')
def djid(djid_id):
    djid = Djid.__registry__[djid_id]
    return {
        'djid': djid,
        'meta': djid._meta,
    }
