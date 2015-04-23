# -*- coding: utf-8 -*-
"""Column definitions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db.models import (
    Count,
    Field,
    ForeignKey,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    IntegerField,
)

from bob.djid.util import PEP3115


if not PEP3115:
    _counter = 0


class Column(object):
    """A column object.
        :param as_link: True or False to force creating links to related object
        If None, the links will be present if ``get_absolute_url`` is defined
    """

    filtered = False
    linking_available = True

    def __init__(self, label, as_link=False):
        global _counter
        self.label = label
        self.as_link = as_link and self.linking_available
        if not PEP3115:
            self.counter = _counter
            _counter += 1

    def get_csv_value(self, model):
        """Returns a 8-bit-safe value for csv."""
        return self.format_label(model).encode('utf-8')

    def format_ajax_value(self, model):
        """Returns a value to be sent via AJAX. It should be an object dumpable
        to JSON."""
        if self.as_link and model and hasattr(model, 'get_absolute_url'):
            return (model.get_absolute_url(), self.format_label(model))
        else:
            return self.format_label(model)

    def get_model(self):
        """Return a dict for jqgrid colModel"""
        result = {"name": self.name}
        if self.as_link:
            result['formatter'] = 'djid_link'
        result['search'] = self.filtered
        return result

    def format_label(self, model):
        """Return the text to be displayed in the cell. To be implemented in
        subclasses"""

    @classmethod
    def from_field(cls, field, Model, *args, **kwargs_override):
        call_kwargs = {
            'label': field.verbose_name.capitalize(),
        }
        if hasattr(Model, 'get_absolute_url'):
            call_kwargs['as_link'] = True
        call_kwargs.update(kwargs_override)
        return cls(**call_kwargs)

    def process_queryset(self, qs):
        """The optional function that allows the column to modify the queryset
        e. g. to prefetch the needed data.
        """
        return qs

    def handle_filters(self, qs, get_dict):
        raise NotImplementedError


class _ColumnRegistry(object):
    """A singleton registry used for per-field column lookup."""

    def __init__(self):
        self._registered = []

    def register(self, field, column, *args, **kwargs):
        """Add a new entry to the registry.
        :param field: A field class or a function returning truish value
            when the field should match
        :param column: A column class or a function that would return a column.
            If a class is provided it is expected to expose a ``from_field``
            classmethod - alternative constructor accepting the field as first
            argument.
        The remaining arguments are passed to the constructor.
        """
        if isinstance(field, type) and issubclass(field, Field):
            def condition(f):
                return isinstance(f, field)
        elif callable(field):
            condition = field
        else:
            raise TypeError(
                '{} is neither a field class nor a function'.format(
                    field
                )
            )
        if isinstance(column, type) and issubclass(column, Column):
            constructor = column.from_field
        elif callable(column):
            constructor = column
        else:
            raise TypeError(
                '{} is neither a column class nor a function'.format(
                    column
                )
            )
        self._registered.insert(0, (condition, constructor, args, kwargs))

    def get_column(self, field, Model):
        """Returns a column for a given field."""
        for condition, constructor, args, kwargs in self._registered:
            if condition(field):
                return constructor(field, Model, *args, **kwargs)
        raise ValueError("No field matched for {}.".format(field))

registry = _ColumnRegistry()


class CharColumn(Column):
    """A simple column that handles character data from a single field."""

    filtered = True

    def format_label(self, model):
        return getattr(model, self.name, '')

    def handle_filters(self, qs, get_dict):
        value = get_dict.get(self.name)
        if value is not None:
            return qs.filter(**{self.name + '__icontains': value})
        else:
            return qs

registry.register(CharField, CharColumn)


class DateTimeColumn(Column):
    """A column that displays datetime using the jqGrid l10n mechanisms."""

    linking_available = False

    def format_label(self, model):
        result = getattr(model, self.name, '') or ''
        return result and result.strftime('%Y-%m-%d %H:%M:%S')

    def get_model(self):
        result = super(DateTimeColumn, self).get_model()
        result.update({'formatter': 'date', 'formatoptions': {
            'srcformat': 'ISO8601Long',
            'newformat': 'ISO8601Long'
        }})
        return result

registry.register(DateTimeField, DateTimeColumn)
registry.register(DateField, DateTimeColumn)


class ForeignColumn(Column):
    """A column that displays the many-to-one related object.
    :param label_field: The field to be used for labels.
    :param label_function: The function to create labels. It receives two
        arguments: the column object and the related object. By default it
        would use ``label_field`` or ``str``
    """

    def __init__(self, label_field=None, label_function=None, *args, **kwargs):
        self.label_field = label_field
        self.label_function = label_function
        super(ForeignColumn, self).__init__(*args, **kwargs)

    def format_label(self, model):
        if self.label_function is not None:
            return self.label_function(self, model)
        elif self.label_field is not None:
            return getattr(model, self.label_field)
        else:
            return str(model)

    def format_ajax_value(self, model):
        return super(ForeignColumn, self).format_ajax_value(
            getattr(model, self.name)
        )

    def process_queryset(self, qs):
        return qs.select_related(self.name)

registry.register(ForeignKey, ForeignColumn)


class NumberColumn(Column):
    """Column for numeric values."""

    filtered = True
    linking_available = False

    def format_label(self, model):
        return str(getattr(model, self.name))

    def handle_filters(self, qs, get_dict):
        value = get_dict.get(self.name)
        if value is None:
            return qs.all()
        for operator, function, suffix in [
                ('<=', qs.filter, '__lte'),
                ('>=', qs.filter, '__gte'),
                ('<>', qs.exclude, ''),
                ('!=', qs.exclude, ''),
                ('==', qs.filter, ''),
                ('>', qs.filter, '__gt'),
                ('<', qs.filter, '__lt'),
                ('=', qs.filter, ''),
        ]:
            if value.startswith(operator):
                return function(**{
                    self.name + suffix:
                    int(value[len(operator):])
                })
        return qs.filter(**{self.name: int(value)})

registry.register(IntegerField, NumberColumn)
registry.register(DecimalField, NumberColumn)


class CountColumn(NumberColumn):
    """A column that counts related one-to-many or many-to-many objects.
    :param relation: The relation to be counted. Without the _set postfix.
    """

    def __init__(self, relation, *args, **kwargs):
        self.relation = relation
        super(CountColumn, self).__init__(*args, **kwargs)

    def process_queryset(self, qs):
        return qs.annotate(**{self.name: Count(self.relation)})
