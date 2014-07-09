# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView


logger = logging.getLogger(__name__)


class BulkEditBase(TemplateView):
    """Base view for bulk edit. This class is very helpful - handle any formset
    from any model. Formset is automaticly generated from model or queryset.
    Additionally you must specified class form for forms which display in
    formset (in simplest case it is ``ModelForm``).

    Example of use:
    .. code-block:: python
        UserBulkEdit(BulkEditBase):
            template_name = 'bulk_edit.html'
            model = User
            form_bulk = UserForm

    or

    .. code-block:: python
        UserBulkEdit(BulkEditBase):
            template_name = 'bulk_edit.html'
            queryset = User.objects.filter(is_active=False)
            form_bulk = UserForm
    """
    commit_on_valid = True
    form_bulk = None
    http_method_names = ['get', 'post']
    ids_key_name = 'select'
    model = None
    queryset = None
    success_url = None
    invalid_url = None

    def initial_forms(self, formset, queryset):
        """Initial forms in formset before render in page. You can manipulate
        fields in forms (eg. change widget, set default value depends on
        queryset, etc).

        :param formset: formset with generated forms
        :param queryset:
        """

    def get(self, request, *args, **kwargs):
        max_bulk_edit_size = getattr(settings, 'MAX_BULK_EDIT_SIZE', 40)
        queryset = self.get_queryset(*args, **kwargs)
        objects_count = queryset.count()
        if not (0 < objects_count <= max_bulk_edit_size):
            if objects_count > max_bulk_edit_size:
                messages.warning(
                    request,
                    _('You can edit max {} items'.format(max_bulk_edit_size)),
                )
            elif not objects_count:
                messages.warning(request, _('Nothing to edit.'))
            return HttpResponseRedirect(self.get_invalid_url())
        FormSet = self.get_formset()
        formset = FormSet(queryset=queryset)
        self.initial_forms(formset, queryset)
        kwargs.update({'formset': formset})
        return self.render_to_response(self.get_context_data(*args, **kwargs))

    def post(self, request, *args, **kwargs):
        FormSet = self.get_formset()
        formset = FormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=self.commit_on_valid)
            if not self.commit_on_valid:
                self.save_formset(instances, formset)
            messages.success(request, _('Changes saved.'))
            return HttpResponseRedirect(self.get_success_url())
        self.handle_formset_error(formset.get_form_error())
        kwargs.update({'formset': formset})
        return self.render_to_response(self.get_context_data(*args, **kwargs))

    def get_context_data(self, *args, **kwargs):
        context = super(BulkEditBase, self).get_context_data(*args, **kwargs)
        context.update(kwargs)
        return context

    def get_success_url(self):
        """Redirect after successfully send formset.

        :return: returns URL (``str``)
        """
        if not self.success_url:
            return self.request.get_full_path()
        return self.success_url

    def get_invalid_url(self):
        """Redirect after send invalid or empty formset.

        :return: returns URL (``str``)
        """
        if not self.invalid_url:
            return '..'
        return self.invalid_url

    def get_form_bulk(self):
        """Attribute form_bulk is required. If yours form is lazy or dynamic
        generated you can override this method.

        :return: standard django form class
        """
        if not self.form_bulk:
            raise ImproperlyConfigured(
                'You must define %(cls)s.form_bulk or override '
                '%(cls)s.get_form_bulk method.' % {
                    'cls': self.__class__.__name__,
                }
            )
        return self.form_bulk

    def get_formset(self, **kwargs):
        kwargs.update({'form': self.get_form_bulk()})
        return modelformset_factory(self.model, extra=0, **kwargs)

    def get_queryset(self, *args, **kwargs):
        if not self.queryset:
            if self.model:
                query = self.get_query_from_request()
                return self.model._default_manager.filter(query)
            else:
                raise ImproperlyConfigured(
                    'You must define %(cls)s.model or %(cls)s.queryset or '
                    'override %(cls)s.get_queryset method.' % {
                        'cls': self.__class__.__name__,
                    }
                )
        return self.queryset._clone()

    def get_query_from_request(self):
        return Q(pk__in=self.get_items_ids())

    def get_items_ids(self):
        """Get ids of object from request parameters."""
        ids = self.request.GET.getlist(self.ids_key_name)
        try:
            int_ids = map(int, ids)
        except ValueError:
            int_ids = []
        return int_ids

    def save_formset(self, instances, formset):
        """If commit_on_valid is set to ``False`` then this method will be
        required. If you override this method you must save instances manually
        (if you want of course).

        .. note::
            Please use context manager ``transaction.commit_on_success()`` from
            ``from django.db import transaction`` where you save instances
            to database.

        :param instances: list of objects
        :param formset: formset
        """
        if not self.commit_on_valid:
            raise ImproperlyConfigured(
                'You must override %(cls)s.save_formset if attribute '
                '%(cls)s.commit_on_valid is set.' % {
                    'cls': self.__class__.__name__
                }
            )

    def handle_formset_error(self, formset_error):
        messages.error(self.request, formset_error)
