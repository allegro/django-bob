class Column(object):
    """A column object."""

    def __init__(self, label):
        self.label = label

    def format_ajax_value(self, model):
        """Returns a value to be sent via AJAX. It should be an object dumpable
        to JSON."""

    def get_model(self):
        """Return a dict for jqgrid colModel"""
        return {"name": self.name}
        

class CharColumn(Column):
    """A simple column that handles character data from a single field."""

    def format_ajax_value(self, model):
        return getattr(model, self.name)


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
