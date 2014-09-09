import collections
import json

from django.core.paginator import Paginator
from django.http import HttpResponse

from bob.djid.column import Column


class DjidMeta(type):
    """A djid metaclass."""
    
    def __init__(cls, clsname, bases, dict_):
        columns = collections.OrderedDict()
        for k, v in dict_.items():
            if isinstance(v, Column):
                v.name = k
                columns[k] = v
        cls.__columns__ = columns
        super(DjidMeta, cls).__init__(clsname, bases, dict_)


class Djid(object):
    """A base djid class. Not meant to be instantiated."""

    __metaclass__ = DjidMeta
    page_size = 20

    @classmethod
    def get_paginator(cls, query_set):
        """Returns a paginator for the queryset."""
        return Paginator(query_set, cls.page_size)

    @classmethod
    def get_full_query_set(cls):
        """Return the whole, unfiltered and unpaginated query set."""
        return cls.query_set

    @classmethod
    def get_filtered_query_set(cls, request):
        """Returns a filtered query set."""
        return cls.get_full_query_set()

    @classmethod
    def format_ajax_row(cls, model):
        """Returns a row formatted for AJAX response."""
        cell = [] 
        for field in cls.__columns__.values():
            cell.append(field.format_ajax_value(model))
        return {'id': model.id, 'cell': cell}

    @classmethod
    def get_ajax_data(cls, request):
        """The AJAX view for this djid."""
        filtered_query_set = cls.get_filtered_query_set(request)
        page = request.GET['page']
        paginator = cls.get_paginator(filtered_query_set)
        rows = []
        for model in paginator.page(page).object_list:
            rows.append(cls.format_ajax_row(model))
        return HttpResponse(
            json.dumps({
                'total': paginator.num_pages,
                'page': page,
                'records': paginator.count,
                'rows': rows,
            }),
            content_type='application/json',
        )

