from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape as esc

from django.utils.timesince import timesince
import datetime

register = template.Library()


@register.simple_tag
def bob_icon(name, is_white=False):
    """
    Display a bootstrap icon.

    :param name: The name of the icon to display.
    :param is_white: Whether the icon should be white (for dark background).
    """

    white = ' icon-white' if is_white else ''
    return mark_safe('<i class="icon-%s%s"></i>' % esc(name, white))


@register.inclusion_tag('bob/main_menu.html')
def main_menu(items, selected, title=None, search=None, white=False,
              position=''):
    """
    Show main menu bar.

    :param items: The list of :class:`bob.menu.MenuItem` instances to show.
    :param selected: The :data:`name` of the currently selected item.
    :param title: The title to show in the menu bar.
    :param search: The URL for the search form.
    :param white: If True, the menu bar will be white.
    :param position: Empty, or one of ``'fixed'``, ``'static'``, ``'bottom'``.
    """

    return {
        'items': items,
        'selected': selected,
        'title': title,
        'search': search,
        'position': position,
        'white': bool(white),
    }

@register.inclusion_tag('bob/tab_menu.html')
def tab_menu(items, selected, side=None):
    """
    Show a menu in form of tabs.

    :param items: The list of :class:`bob.menu.MenuItem` instances to show.
    :param selected: The :data:`name` of the currently selected item.
    :param side: The direction of tabs, may be on of ``"left"``, ``"right"``,
        ``"top"`` or ``"bottom"``. Defaults to ``"top"``.
    """

    return {
        'items': items,
        'selected': selected,
        'side': side,
    }

@register.inclusion_tag('bob/sidebar_menu.html')
def sidebar_menu(items, selected):
    """
    Show menu in a sidebar.

    :param items: The list of :class:`bob.menu.MenuItem` instances to show.
    :param selected: The :data:`name` of the currently selected item.
    """

    return {
        'items': items,
        'selected': selected,
    }

@register.inclusion_tag('bob/sidebar_menu_subitems.html')
def sidebar_menu_subitems(item, selected):
    """
    Show subitems of a menu in a sidebar.
    """

    return {
        'item': item,
        'selected': selected,
    }

@register.inclusion_tag('bob/pagination.html')
def pagination(page, show_all=False, show_csv=False,
                fugue_icons=False, url_query=None, neighbors=1):
    """
    Display pagination for a list of items.

    :param page: Django's paginator page to display.
    :param show_all: Whether to show a link for disabling pagination.
    :param show_csv: Whether to show a link to CSV download.
    :param fugue_icons: Whether to use Fugue icons or Bootstrap icons.
    :param url_query: The query parameters to add to all page links.
    :param neighbors: How many neighboring pages to show in paginator.
    """

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

    :param d: The date to display.
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

