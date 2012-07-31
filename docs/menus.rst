Menus
*****

The menu definition
-------------------

.. module:: bob.menu

Menus in Bob are defined as collections of :class:`MenuItem` and
:class:`Separator` instances. Each :class:`MenuItem` defines one entry in the
menu. A :class:`Separator` defines a spacing, line or other way of separating
groups of related items -- depending on the kind of the menu used.


.. autoclass:: MenuItem
    :members:

.. autoclass:: Separator
    :members:

The menu tags
-------------

.. module:: bob.templatetags.bob

Once you have the menu items defined, you can display them in your templates
using one of several menu tags.


.. autofunction:: main_menu
.. autofunction:: tab_menu
.. autofunction:: sidebar_menu
