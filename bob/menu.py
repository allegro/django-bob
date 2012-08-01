from django.core.urlresolvers import reverse

class MenuItem(object):
    """
    A container object for all the information about a single menu item.

    :param label: The label to be displayed for this menu item. Required.

    :param name: The symbolic name used in class names, ids and selections.
        If not specified, it is generated from the :attr:`label`.

    :param subitems: The list of :class:`MenuItem` instances for nested
        menus in :func:`bob.templatetags.bob.sidebar_menu` .

    :param href: The URL to which this menu item should link.
    :param view_name: The name of the URL rule to which this item should link.
    :param view_args: The positional arguments for the URL rule.
    :param view_kwargs: The keyword arguments for the URL rule.
    :param icon: A Bootstrap icon to show for this item.
    :param fugue_icon: A Fugue icon to show for this item, if available.
    :param collapsible: Whether the submenu should be collapsible. Default ``False``.
    :param collapsed: Whether the submenu should start collapsed. Default ``False``.
    :param indent: A string by which the item should be indented.
    """

    item_kind = 'link'

    def __init__(self, label, name=None, subitems=None, **kwargs):
        """
        """
        self.label = label
        if name is None:
            self.name = label.lower()
        else:
            self.name = name
        self.subitems = subitems
        self.kwargs = kwargs

    def get_href(self):
        href = self.kwargs.get('href')
        if href:
            return href
        view_name = self.kwargs.get('view_name')
        view_args = self.kwargs.get('view_args', [])
        view_kwargs = self.kwargs.get('view_kwargs', {})
        if view_name:
            return reverse(view_name, args=view_args, kwargs=view_kwargs)
        return ''


class Separator(object):
    """Show a separator in menus."""

    item_kind = 'separator'


class MenuHeader(object):
    """
    Show a header in menus.

    :param label: The text to display in the header.
    """

    item_kind = 'header'

    def __init__(self, label):
        self.label = label

