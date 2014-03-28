# -*- coding: utf-8 -*-
"""All the objects needed to use the dependency mechanism"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from bob.forms.dependency_conditions import DependencyCondition


# dependencies types
SHOW = 'SHOW'
REQUIRE = 'REQUIRE'
AJAX_UPDATE = 'AJAX_UPDATE'


class Dependency(object):
    """The single dependency: if master has value then do action on slave.

    If action is ``AJAX_UPDATE`` you have to set `url` kwarg. Url corresponds
    to
    :py:class:bob.views.dependency.DependencyView
    subclass.
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
        """Return true if condition is met."""
        val = data.get(self.master)
        return self.condition.met(val)


class DependencyForm(object):  # Can't inherit Form due to metaclass conflict
    """Form mixin with dependency feature."""

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
