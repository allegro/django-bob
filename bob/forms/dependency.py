# -*- coding: utf-8 -*-
"""All the objects needed to use the dependency mechanism"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple, Container

from django.db.models import Model
from django.utils.translation import ugettext as _


SHOW = 'SHOW'
REQUIRE = 'REQUIRE'
AJAX_UPDATE = 'AJAX_UPDATE'


Dependency = namedtuple('Dependency', ('slave', 'master', 'value', 'action'))


class Dependency(object):
    """The single dependency: if master has value then do action on slave.

    If action is ``AJAX_UPDATE`` you have to set `url` kwarg. Url corresponds
    to
    :py:class:bob.views.dependency.DependencyView
    subclass.
    """

    def __init__(self, slave, master, value, action, **options):
        self.slave = slave
        self.master = master
        self.value = value
        self.action = action
        self.options = options
        if action == AJAX_UPDATE:
            assert 'url' in options, "Source url not provided."

    def met(self, data):
        """Return true if condition is met."""
        val = data.get(self.master)
        if val is None:
            return False
        if isinstance(self.value, Container):
            return val in self.value
        else:
            return val == self.value


class DependencyForm(object):  # Can't inherit Form due to metaclass conflict
    """Form mixin with dependency feature."""

    dependencies = []

    def clean(self):
        cleaned_data = super(DependencyForm, self).clean()
        for dep in self.dependencies:
            if dep.met(cleaned_data):
                if dep.action == REQUIRE:
                    if not self.data.get(dep.slave):
                        msg = _("This field is required")
                        self._errors[dep.slave] = self.error_class([msg])
            else:
                if dep.action in {SHOW}:
                    self._errors.pop(dep.slave, None)
        return cleaned_data

    def _format_single_val_for_js(self, val):
        """Return the appropriate js representation of a single value."""
        if val is None:
            return val
        if not isinstance(val, str):
            if isinstance(val, Model):
                val = val.id
            val = str(val)
        return val

    def get_dependencies_for_js(self):
        """Return the dependencies in a format ready to be JSON serialized for
        JavaScript"""
        result = []
        for dep in self.dependencies:
            if isinstance(dep.value, Container):
                value = [self._format_single_val_for_js(v) for v in dep.value]
            else:
                value = self._format_single_val_for_js(dep.value)
            result.append({
                'slave': dep.slave,
                'master': dep.master,
                'value': value,
                'action': dep.action,
                'options': dep.options
            })
        return result
