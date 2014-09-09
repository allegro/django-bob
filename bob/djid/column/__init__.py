class Column(object):
    """A column object."""

class CharColumn(Column):
    """A simple column that handles character data from a single field."""

    def format_ajax_value(self, model):
        """Returns a value to be sent via AJAX. It should be an object dumpable
        to JSON."""
        return getattr(model, self.name)
