from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape as esc


register = template.Library()


@register.simple_tag
def bob_icon(name, is_white=False):
    white = ' icon-white' if is_white else ''
    return mark_safe('<i class="icon-%s%s"></i>' % esc(name, white))


@register.inclusion_tag('bob/main_menu.html')
def main_menu(items, selected, title=None, search=None):
    return {
        'items': items,
        'selected': selected,
        'title': title,
        'search': search,
    }

@register.inclusion_tag('bob/tab_menu.html')
def tab_menu(items, selected):
    return {
        'items': items,
        'selected': selected,
    }
