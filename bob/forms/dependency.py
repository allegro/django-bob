# -*- coding: utf-8 -*-
"""All the objects needed to use the dependency mechanism"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple, Container

from django.db.models import Model

SHOW = 'SHOW'

Dependency = namedtuple('Dependency', ('slave', 'master', 'value', 'action'))

class Dependency(object):
    """The single dependency: if master has value then do action on slave."""

    def __init__(self, slave, master, value, action):
        self.slave = slave
        self.master = master
        self.value = value
        self.action = action

    def met(self, data):
        """Return true if condition is met."""
        val = data[self.master]
        if isinstance(self.value, Container):
            return val in self.value
        else:
            return val == self.value

class DependencyForm(object): # Can't inherit Form due to metaclass conflict
    """Form mixin with dependency feature."""

    dependencies = []

    def clean(self):
        data = super(DependencyForm, self).clean()
        for dep in self.dependencies:
            if not dep.met(data):
                if dep.action == 'SHOW':
                    del self._errors[dep.slave]
        return data
    
    def _format_single_val_for_js(self, val):
        """Return the appropriate js representation of a single value."""
        if isinstance(val, Model):
            return str(val.id)
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
                'slave': dep.slave, 'master': dep.master,
                'value': value, 'action': dep.action})
        return result
