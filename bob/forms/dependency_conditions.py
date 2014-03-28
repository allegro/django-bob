# -*- coding: utf-8 -*-
from collections import Container

from django.db.models import Model


def format_single_val_for_js(val):
    """Return the appropriate js representation of a single value."""
    # null, true and false are correct json values
    if not (val is None or isinstance(val, bool)):
        if isinstance(val, Model):
            val = val.pk
        if not isinstance(val, basestring):
            val = str(val)
    return val


def format_val_for_js(val):
    if not isinstance(val, basestring) and isinstance(val, Container):
        val = map(format_single_val_for_js, val)
    else:
        val = format_single_val_for_js(val)
    return val


def first_letter_lower(name):
    return name[0].lower() + name[1:]


class DependencyCondition(object):
    """Each dependency should have defined trigger condition.
    """
    def met(self, value):
        raise NotImplementedError

    def get_js_format(self):
        return [first_letter_lower(self.__class__.__name__)]


class ArgumentedCondition(DependencyCondition):
    def __init__(self, value):
        self.value = value

    def get_js_format(self):
        format = super(ArgumentedCondition, self).get_js_format()
        format.append(format_val_for_js(self.value))
        return format


###############################################################################
# Real conditions here:
###############################################################################


class Any(DependencyCondition):
    def met(self, val):
        return True


class Exact(ArgumentedCondition):
    def met(self, val):
        return format_val_for_js(self.value) == format_val_for_js(val)


class MemberOf(ArgumentedCondition):
    def met(self, val):
        return format_val_for_js(val) in format_val_for_js(self.value)


class NotEmpty(DependencyCondition):
    def met(self, val):
        return val != "" and val is not None
