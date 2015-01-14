# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from bob.djid import Djid
from bob.djid.column import CountColumn
from bob.test_djid.models import Person, Company

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView


class PersonsGrid(Djid):
    """A grid displaying persons."""

    class Meta:
        djid_id = 'persons'
        Model = Person
        columns = [
            'first_name',
            'last_name',
            'registered',
            'score',
            'company',
        ]


class CompanyGrid(Djid):
    class Meta:
        djid_id = 'companies'
        Model = Company
        columns = ['name', 'phone', 'person_count']

    person_count = CountColumn(relation='person', label='Persons')


class DisplayDjid(TemplateView):

    template_name = 'display_djid.html'

    def get_context_data(self, djid, *args, **kwargs):
        ret = super(DisplayDjid, self).get_context_data(*args, **kwargs)
        ret['djid_id'] = djid
        return ret


class PersonView(TemplateView):

    template_name = 'person.html'

    def get_context_data(self, person_id, *args, **kwargs):
        person = get_object_or_404(Person, pk=person_id)
        return {'person': person}


class CompanyView(TemplateView):

    template_name = 'company.html'

    def get_context_data(self, company_id, *args, **kwargs):
        company = get_object_or_404(Company, pk=company_id)
        return {'company': company}
