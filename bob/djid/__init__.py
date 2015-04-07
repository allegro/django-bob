# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections
import csv
import io
import json
import types

import django_rq
import rq
from django.conf.urls import patterns, url
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.conf import settings

from bob.djid.column import Column, registry
from bob.djid.util import PEP3115


class DefaultMeta(object):
    """Default Meta for a Djid"""


class DjidMeta(type):
    """A djid metaclass."""

    __registry__ = {}
    queue_name = (
        'djid_reports' if 'djid_reports' in settings.RQ_QUEUES else 'default'
    )
    queue = django_rq.get_queue(queue_name)
    connection = django_rq.get_connection(queue_name)

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

        meta.additional_params = getattr(meta, 'additional_params', None)

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
    def view_decorator(cls, view):
        return view # noop


    @classmethod
    def get_paginator(cls, query_set):
        """Returns a paginator for the queryset."""
        return Paginator(query_set, cls.page_size)

    @classmethod
    def get_full_query_set(cls):
        """Return the whole, unfiltered and unpaginated query set."""
        queryset = cls._meta.Model.objects
        queryset = reduce(
            lambda qs, col: col.process_queryset(qs),
            cls._meta.column_dict.values(),
            queryset,
        )
        return queryset

    @classmethod
    def get_filtered_query_set(cls, request):
        """Returns a filtered and ordered query set."""
        queryset = cls.get_full_query_set()
        queryset = reduce(
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
    def get_export_data(cls, djid, query_set, content_type):
        """Returns a tuple of content_type, result. Meant to be called by the
        enqueued function."""
        return (
            content_type,
            {
                'text/csv': cls.get_export_data_csv,
            }[content_type](query_set)
        )

    @classmethod
    def get_export_data_csv(cls, filtered_query_set):
        buf = io.BytesIO()
        writer = csv.writer(buf)
        writer.writerow([
            column.label.encode('utf-8')
            for column in cls._meta.column_dict.values()
        ])
        for model in filtered_query_set:
            writer.writerow([
                column.get_csv_value(model)
                for column in cls._meta.column_dict.values()
            ])
        return buf.getvalue()

    @classmethod
    def start_report(cls, request):
        filtered_query_set = cls.get_filtered_query_set(request)
        content_type = request.META['HTTP_ACCEPT']
        job = cls.queue.enqueue_call(
            func=make_report,
            args=(cls, filtered_query_set.query, content_type),
            timeout=3000,
        )
        return cls.get_status_response(job)

    @classmethod
    def update_status(cls, request):
        job = rq.job.Job.fetch(
            request.GET['job_id'], connection=cls.connection
        )
        return cls.get_status_response(job)

    @classmethod
    def get_status_response(cls, job):
        return HttpResponse(json.dumps({
            'job_id': job.id,
            'finished': job.result is not None,
            'exc_info': job.exc_info,
        }), mimetype='application/json')

    @classmethod
    def get_report(cls, request):
        job = rq.job.Job.fetch(
            request.GET['job_id'], connection=cls.connection
        )
        content_type, result = job.result
        return HttpResponse(result, content_type=content_type)

    @classmethod
    def dispatcher(cls, request, djid_id, action):
        """Dispatching view that passes control to appropriate method in
        an appropriate djid"""
        djid = cls.__registry__[djid_id]
        # No. Removing the dictionary below is not a good idea, as it will
        # allow user to call any method of djid
        method = getattr(djid, {
            'get_ajax': 'get_ajax_data',
            'start_report': 'start_report',
            'update_status': 'update_status',
            'get_report': 'get_report',
        }[action])
        
        # We decorate a function  not a method, so we need to unwrap it and
        # rewrap it again
        decorated_method = types.MethodType(
            djid.view_decorator(method.im_func),
            method.im_self,
            method.im_class,
        )
        return decorated_method(request)

    @classmethod
    def resolver(cls):
        """The URL resolve list that should be included in URLconf"""
        return patterns(
            '',
            url(
                r'^(?P<action>start_report|update_status|get_report)'
                '/(?P<djid_id>[A-Za-z0-9-]+)/$',
                cls.dispatcher,
            ),
            url(
                r'^(?P<djid_id>[A-Za-z0-9-]+)/$',
                cls.dispatcher,
                {'action': 'get_ajax'},
            ),
        )

    @classmethod
    def col_names(cls):
        return [column.label for column in cls._meta.column_dict.values()]

    @classmethod
    def col_model(cls):
        return [
            column.get_model() for column in cls._meta.column_dict.values()
        ]

    @classmethod
    def additional_params(cls):
        return cls._meta.additional_params

    @classmethod
    def get_params(cls):
        ret = {
            'colNames': cls.col_names(),
            'colModel': cls.col_model(),
            'rowNum': cls.page_size
        }
        ret.update(cls.additional_params())
        return json.dumps(ret)


def make_report(djid, query, content_type):
    queryset = djid._meta.Model.objects.all()
    queryset.query = query
    return djid.get_export_data(djid, queryset, content_type)
