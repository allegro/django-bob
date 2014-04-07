# -*- coding: utf-8 -*-
"""All the objects needed to use the dependency mechanism.

For dependency usage you need to:

* add :class:`DependencyForm` as your form mixin,
* (optional) define :class:`bob.views.dependency.DependencyView` if
  :const:`AJAX_UPDATE` used.
* define ``dependencies`` property in you form.

``dependencies`` example:

.. code-block:: python

    @property
    def dependencies(self):
        return [
            Dependency(
                'slots',
                'category',
                dependency_conditions.MemberOf(
                    AssetCategory.objects.filter(is_blade=True).all()
                ),
                SHOW,
            ),
            Dependency(
                'location',
                'owner',
                dependency_conditions.NotEmpty(),
                AJAX_UPDATE,
                url=reverse('category_dependency_view'),
                page_load_update=False,
            )
        ]
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from bob.forms.dependency_conditions import DependencyCondition


# dependencies types
AJAX_UPDATE = 'AJAX_UPDATE'
"""Load slave value by ajax request if master value met condition."""
CLONE = 'CLONE'
"""Copy master value to slave value."""
SHOW = 'SHOW'
"""Show slave field if master value met condition."""
REQUIRE = 'REQUIRE'
"""Set slave value required."""


class Dependency(object):
    """The single dependency.

    If action is :const:`AJAX_UPDATE` you have to set ``url`` kwarg. Url
    corresponds to :class:`bob.views.dependency.DependencyView` subclass.

    :param slave: Dependency target field.
    :param master: Dependency source field. It's value is condition param.
    :param condition: :class:`.dependency_conditions.DependencyCondition`
        subclass.
    :param action: One of :const:`AJAX_UPDATE`, :const:`CLONE`,
        :const:`SHOW`, :const:`REQUIRE`.
    :param \*\*options: Another options, like ``url`` if action is
        :const:`AJAX_UPDATE`.
    """

    def __init__(self, slave, master, condition, action, **options):
        self.slave = slave
        self.master = master
        self.condition = condition
        assert isinstance(condition, DependencyCondition)
        self.action = action
        self.options = options
        self.options['page_load_update'] = options.get(
            'page_load_update', True,
        )
        if action == AJAX_UPDATE:
            assert 'url' in options, "Source url not provided."

    def met(self, data):
        """Return ``True`` if condition is met.

        :param data: form.cleaned_data dictionary with master field value.
        """
        val = data.get(self.master)
        return self.condition.met(val)


class DependencyForm(object):  # Can't inherit Form due to metaclass conflict
    """Form mixin with dependency feature.

    It should be used in django forms which includes dependencies.
    It provides clean method with dependencies validation.
    """

    dependencies = []

    def clean(self):
        cleaned_data = super(DependencyForm, self).clean()
        for dep in self.dependencies:
            if dep.met(cleaned_data):
                if dep.action == REQUIRE:
                    unfilled = (
                        dep.slave in cleaned_data and not
                        cleaned_data[dep.slave]
                    )
                    if unfilled:
                        msg = _("This field is required")
                        self._errors[dep.slave] = self.error_class([msg])
            else:
                if dep.action in {SHOW}:
                    self._errors.pop(dep.slave, None)
        return cleaned_data

    def get_dependencies_for_js(self):
        """Return the dependencies in a format ready to be JSON serialized for
        JavaScript"""
        result = []
        for dep in self.dependencies:
            result.append({
                'slave': dep.slave,
                'master': dep.master,
                'condition': dep.condition.get_js_format(),
                'action': dep.action,
                'options': dep.options
            })
        return result
