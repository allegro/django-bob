# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import datetime

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape as esc
from django.utils.timesince import timesince
from bob.forms.dependency import DependencyForm


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
              position='', title_url="/"):
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
        'title_url': title_url,
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
               fugue_icons=False, url_query=None, neighbors=1,
               query_variable_name='page', export_variable_name='export'):
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
            'export_variable_name': export_variable_name,
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
    urls = []
    for item in pages:
        if item == '...':
            urls.append(changed_url(url_query, query_variable_name, page_no))
        else:
            urls.append(changed_url(url_query, query_variable_name, item))
    url_pages = zip(pages, urls)
    return {
        'paginator': paginator,
        'page_no': page_no,
        'page': page,
        'pages': pages,
        'show_all': show_all,
        'show_csv': show_csv,
        'fugue_icons': fugue_icons,
        'url_query': url_query,
        'url_previous_page': changed_url(url_query, query_variable_name, page_no-1),
        'url_next_page': changed_url(url_query, query_variable_name, page_no+1),
        'url_pages': url_pages,
        'url_all': changed_url(url_query, query_variable_name, 0),
        'export_variable_name': export_variable_name,
    }


def changed_url(query, name, value):
    if not query:
        return '%s=%s' % (name, value)
    query = query.copy()
    if value is not None and value not in ('1', 1):
        query[name] = value
    else:
        try:
            del query[name]
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
    today = datetime.datetime.now()
    delta = datetime.timedelta
    interval = today - d
    if today.strftime('%Y-%m-%d') == d.strftime('%Y-%m-%d'):
        if interval < delta(days=0, hours=1):
            return timesince(d) + ' ago '
        else:
            return d.strftime('%H:%M')
    else:
        return d


@register.inclusion_tag('bob/form.html')
def form(form, action="", method="POST", fugue_icons=False,
         css_class="form-horizontal", title="", submit_label='Save'):
    """
    Render a form.

    :param form: The form to render.
    :param action: The submit URL.
    :param method: The submit method, either ``"GET"`` or ``"POST"``.
    :param fugue_icons: Whether to use Fugue or Bootstrap icon.
    :param css_class: The CSS class to use for the ``<form>`` tag.
    :param title: Form title.
    :param submit_label: Submit button label.
    """
    return {
        'form': form,
        'action': action,
        'title': title,
        'method': method,
        'fugue_icons': fugue_icons,
        'css_class': css_class,
        'submit_label': submit_label,
    }


@register.inclusion_tag('bob/form.html')
def form_horizontal(*args, **kwargs):
    return form(*args, **kwargs)


@register.inclusion_tag('bob/table_header.html')
def table_header(columns=None, url_query=None, sort=None, fugue_icons=False,
                 sort_variable_name='sort'):
    """
    Render a table header with sorted column options

    :param columns: a list of objects of
                    type :py:class:bob.data_table.DataTableColumn
    :param url_query: The query parameters to add to all page links
    :param sort: means that the column is now sorted
    :param fugue_icons: Whether to use Fugue icons or Bootstrap icons.

    """
    return {
        'columns': columns,
        'sort': sort,
        'url_query': url_query,
        'fugue_icons': fugue_icons,
        'sort_variable_name': sort_variable_name,
    }

@register.simple_tag
def bob_sort_url(query, field, sort_variable_name, type):
    """Modify the query string of an URL to change the ``sort_variable_name``
    argument.
    """
    query = query.copy()
    if type == 'desc':
        query[sort_variable_name] = '-' + field
    elif type == 'asc':
        query[sort_variable_name] = field
    return query.urlencode()

@register.simple_tag
def bob_export_url(query, value, export_variable_name='export'):
    """Modify the query string of an URL to change the ``export_variable_name``
    argument.
    """
    if not query:
        return '%s=%s' % (export_variable_name, value)
    query = query.copy()
    if value:
        query[export_variable_name] = value
    else:
        try:
            del query[export_variable_name]
        except KeyError:
            pass
    return query.urlencode()

@register.simple_tag
def dependency_data(form):
    """Render the data-bob-dependencies tag if this is a DependencyForm"""

    if not isinstance(form, DependencyForm):
        return ''
    return 'data-bob-dependencies="{0}"'.format(
        esc(json.dumps(form.get_dependencies_for_js())))
