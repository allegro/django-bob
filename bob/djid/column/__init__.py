from django.db.models.fields import Field, CharField, DateTimeField
from bob.djid.util import PEP3115


if not PEP3115:
    _counter = 0


class Column(object):
    """A column object."""

    def __init__(self, label):
        global _counter
        self.label = label
        if not PEP3115:
            self.counter = _counter
            _counter += 1

    def format_ajax_value(self, model):
        """Returns a value to be sent via AJAX. It should be an object dumpable
        to JSON."""

    def get_model(self):
        """Return a dict for jqgrid colModel"""
        return {"name": self.name}

    @classmethod
    def from_field(cls, field, *args, **kwargs_override):
        call_kwargs = {
            'label': field.verbose_name.capitalize(),
        }
        call_kwargs.update(kwargs_override)
        return cls(label=field.verbose_name.capitalize())


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
            condition = lambda f: isinstance(f, field)
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

    def get_column(self, field):
        """Returns a column for a given field."""
        for condition, constructor, args, kwargs in self._registered:
            if condition(field):
                return constructor(field, *args, **kwargs)
        raise ValueError("No field matched for {}.".format(field))

registry = _ColumnRegistry()


class CharColumn(Column):
    """A simple column that handles character data from a single field."""

    def format_ajax_value(self, model):
        return getattr(model, self.name)

registry.register(CharField, CharColumn)


class DateTimeColumn(Column):
    """A column that displays datetime using the jqGrid l10n mechanisms."""

    def format_ajax_value(self, model):
        return getattr(model, self.name).isoformat()

    def get_model(self):
        result = super(DateTimeColumn, self).get_model()
        result.update({'formatter': 'date', 'formatoptions': {
            'newformat': 'SortableDateTime'
        }})
        return result

registry.register(DateTimeField, DateTimeColumn)
