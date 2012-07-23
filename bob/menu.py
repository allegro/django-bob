from django.core.urlresolvers import reverse

class MenuItem(object):
    """A container object for all the information aboout single menu item."""

    item_kind = 'link'

    def __init__(self, label, name=None, subitems=None, **kwargs):
        self.label = label
        self.name = name or label.lower()
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
    """Draws a separator in menus."""

    item_kind = 'separator'
