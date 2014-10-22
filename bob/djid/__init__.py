import collections
import json

from django.core.paginator import Paginator
from django.http import HttpResponse

from bob.djid.column import Column, registry
from bob.djid.util import PEP3115


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
        def mount_column(k, v):
            v.name = k
            column_dict[k] = v
        # I add getattr very reluctantly here, as this is prone to The Great
        # Python Design Flaw. But one can use generators instead of properties
        # so it shouldn't be the case here
        columns = getattr(meta, 'columns', None)
        if columns:
            cls.init_from_list(meta, columns, dict_, mount_column)
        else:
            cls.init_from_dict(dict_, mount_column)
        meta.column_dict = column_dict
        try:
            cls.__registry__[meta.djid_id] = cls
        except AttributeError:
            pass
        super(DjidMeta, cls).__init__(clsname, bases, dict_)
        cls._meta = meta

    def init_from_list(cls, meta, columns, dict_, mount_column):
        for column_name in columns:
            if column_name in dict_:
                mount_column(column_name, dict_[column_name])
            else:
                field = meta.Model._meta.get_field(column_name)
                mount_column(column_name, registry.get_column(
                    field, meta.Model
                ))

    def init_from_dict(cls, dict_, mount_column):
        """Mounts the colummns from class dict. Used when no column list
        is provided."""
        if PEP3115:
            for k, v in dict_.items():
                if isinstance(v, Column):
                    mount_column(k, v)
        else:
            dict_columns = [
                (k, v) for k, v in dict_.items() if isinstance(v, Column)
            ]
            dict_columns.sort(key=lambda item: item[1].counter)
            for k, v in dict_columns:
                mount_column(k, v)

    def __prepare__(cls, name, bases):
        return collections.OrderedDict()


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
        queryset = cls._meta.Model.objects
        queryset = reduce (
            lambda qs, col: col.process_queryset(qs),
            cls._meta.column_dict.values(),
            queryset,
        )
        return queryset

    @classmethod
    def get_filtered_query_set(cls, request):
        """Returns a filtered and ordered query set."""
        queryset = cls.get_full_query_set()
        queryset = reduce (
            lambda qs, col: (
                col.handle_filters(qs, request.GET)
                if col.filtered
                else qs
            ),
            cls._meta.column_dict.values(),
            queryset,
        )
        
        order_string = (
            request.GET.get('sidx', '') +
            request.GET.get('sord', '')
        )
        if order_string and order_string != ' ':
            order_pairs = zip(*([iter(order_string.split(' '))] * 2))
            order_args = [
                ('-' if direction == 'desc' else '') + column
                for column, direction in order_pairs
            ]
            queryset = queryset.order_by(*order_args)
        else:
            queryset = queryset.all()
        return queryset

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
