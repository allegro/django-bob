# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import forms
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.utils.html import escape
from django.utils import simplejson as json

class AutocompleteWidget(forms.Select):
    """A choice widget using a text field with Bootstrap's autocomplete."""

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        labels = dict(self.choices)
        output = [
            u'<input type="text" autocomplete="off" data-provide="typeahead" data-items="10" data-source="%s" value="%s" %s>' % (
                escape(json.dumps(labels.values())),
                escape(labels.get(value, value)),
                flatatt(final_attrs))
        ]
        return mark_safe('\n'.join(output))

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if value == '---------':
            return None
        values = dict((label, value) for value, label in self.choices )
        return values.get(value, value)


class DateTimeWidget(forms.DateInput):
    """A datetime widget using the HTML5 date picker."""

    input_type = 'datetime'

