# vim: set fileencoding=utf-8
from bob.djid import Djid
from bob.djid.column import CharColumn, DateTimeColumn, ForeignColumn
from bob.test_djid.models import Person, Company

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView


class PersonsGrid(Djid):

    class Meta:
        djid_id = 'persons'
        Model = Person


    first_name = CharColumn(label='Imię', as_link=True)
    last_name = CharColumn(label='Nazwisko', as_link=True)
    registered = DateTimeColumn(label='Zarejestrowany')
    company = ForeignColumn(label='Firma', label_field='name', as_link=True)


class Homepage(TemplateView):

    template_name = 'homepage.html'


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
