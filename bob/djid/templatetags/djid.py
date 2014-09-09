from django import template

from bob.djid import Djid


register = template.Library()


@register.inclusion_tag('djid.html')
def djid(djid_id):
    return {'meta': Djid.__registry__[djid_id]._meta}
