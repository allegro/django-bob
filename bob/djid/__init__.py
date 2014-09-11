import collections
import json

from django.core.paginator import Paginator
from django.http import HttpResponse

from bob.djid.column import Column

class DefaultMeta(object):
    """Default Meta for a Djid"""


class DjidMeta(type):
    """A djid metaclass."""

    __registry__ = {}
    
    def __init__(cls, clsname, bases, dict_):
        column_dict = collections.OrderedDict()
        meta = dict_.get('Meta')
        if not meta:
            meta = DefaultMeta()
        for k, v in dict_.items():
            if isinstance(v, Column):
                v.name = k
                column_dict[k] = v
        meta.column_dict = column_dict
        if meta:
            try:
                cls.__registry__[meta.djid_id] = cls
            except AttributeError:
                pass
        super(DjidMeta, cls).__init__(clsname, bases, dict_)
        cls._meta = meta


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
        """Returns a filtered and ordered query set."""
        query_set = cls.get_full_query_set()
        order_string = request.GET['sidx'] + request.GET['sord']
        if order_string != ' ':
            order_pairs = zip(*([iter(order_string.split(' '))] * 2))
            order_args = [
                ('-' if direction == 'desc' else '') + column
                for column, direction in order_pairs
            ]
            query_set = query_set.order_by(*order_args)
        return query_set

    @classmethod
    def format_ajax_row(cls, model):
        """Returns a row formatted for AJAX response."""
        cell = [] 
        for field in cls._meta.column_dict.values():
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

    @classmethod
    def dispatcher(cls, request, djid_id):
        """Dispatching view that passes control to get_ajax_data in
        an appropriate djid"""
        return cls.__registry__[djid_id].get_ajax_data(request)

    @classmethod
    def col_names(cls):
        return json.dumps([
            column.label for column in cls._meta.column_dict.values()
        ])

    @classmethod
    def col_model(cls):
        return json.dumps([
            column.get_model() for column in cls._meta.column_dict.values()
        ])
