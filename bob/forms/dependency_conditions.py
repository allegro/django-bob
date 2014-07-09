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
    """Base abstract class for each dependency.

    It should have defined met function and get_js_format if it's unusual.
    """
    def met(self, value):
        """Return ``True`` if value met condition.

        :param value: master field value.
        """
        raise NotImplementedError

    def get_js_format(self):
        """Return list with condition definition."""
        return [first_letter_lower(self.__class__.__name__)]


class ArgumentedCondition(DependencyCondition):
    """Abstract class for condition with argument."""
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
    """Condition for any ``master.value`` (even empty)."""
    def met(self, val):
        return True


class Exact(ArgumentedCondition):
    """Condition for ``master.value`` equals ``value``."""
    def met(self, val):
        return format_val_for_js(self.value) == format_val_for_js(val)


class MemberOf(ArgumentedCondition):
    """Condition for ``master.value`` is in ``value``."""
    def met(self, val):
        return format_val_for_js(val) in format_val_for_js(self.value)


class NotEmpty(DependencyCondition):
    """Condition for ``master.value`` is not empty."""
    def met(self, val):
        return val != "" and val is not None
