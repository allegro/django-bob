from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape as esc

from django.utils.timesince import timesince
import datetime

register = template.Library()


@register.simple_tag
def bob_icon(name, is_white=False):
    """Display a bootstrap icon."""

    white = ' icon-white' if is_white else ''
    return mark_safe('<i class="icon-%s%s"></i>' % esc(name, white))


@register.inclusion_tag('bob/main_menu.html')
def main_menu(items, selected, title=None, search=None):
    """Show main menu bar."""

    return {
        'items': items,
        'selected': selected,
        'title': title,
        'search': search,
    }

@register.inclusion_tag('bob/tab_menu.html')
def tab_menu(items, selected):
    """Show a menu in form of tabs."""

    return {
        'items': items,
        'selected': selected,
    }

@register.inclusion_tag('bob/sidebar_menu.html')
def sidebar_menu(items, selected):
    """Show menu in a sidebar."""

    return {
        'items': items,
        'selected': selected,
    }

@register.inclusion_tag('bob/pagination.html')
def pagination(page, show_all=False, show_csv=False,
                fugue_icons=False, url_query=None, neighbors=1):
    """Display pagination for a list of items."""

    if not page:
        return {
            'show_all': show_all,
            'show_csv': show_csv,
            'fugue_icons': fugue_icons,
            'url_query': url_query,
        }
    paginator = page.paginator
    page_no = page.number
    pages = paginator.page_range[max(0, page_no - 1 - neighbors):
                                 min(paginator.num_pages, page_no + neighbors)]
    if 1 not in pages:
        pages.insert(0, 1)
        pages.insert(1, '...')
    if paginator.num_pages not in pages:
        pages.append('...')
        pages.append(paginator.num_pages)
    return {
        'paginator': paginator,
        'page_no': page_no,
        'page': page,
        'pages': pages,
        'show_all': show_all,
        'show_csv': show_csv,
        'fugue_icons': fugue_icons,
        'url_query': url_query,
    }

@register.filter
def bob_page(query, page):
    """Modify the query string of an URL to change the ``page`` argument."""

    if not query:
        return 'page=%s' % page
    query = query.copy()
    if page is not None and page not in ('1', 1):
        query['page'] = page
    else:
        try:
            del query['page']
        except KeyError:
            pass
    return query.urlencode()

@register.filter
def bob_export(query, export):
    """Modify the query string of an URL to change the ``export`` argument."""

    if not query:
        return 'export=%s' % export
    query = query.copy()
    if export:
        query['export'] = export
    else:
        try:
            del query['export']
        except KeyError:
            pass
    return query.urlencode()


@register.filter
def timesince_limited(d):
    """
    Display time between given date and now in a human-readable form if the
    time span is less than a day, otherwise display the date normally.
    """
    interval = datetime.datetime.now() - d
    delta = datetime.timedelta
    if interval < delta(days=1):
        if interval < delta(days=0, hours=1):
            return timesince(d) + ' ago '
        else:
            return d.strftime('%H:%M')
    else:
        return d

