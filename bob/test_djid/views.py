# vim: set fileencoding=utf-8
from bob.djid import Djid
from bob.djid.column import CharColumn, DateTimeColumn
from bob.test_djid.models import Person

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView


class PersonsGrid(Djid):

    class Meta:
        djid_id = 'persons'

    query_set = Person.objects.all()

    first_name = CharColumn(label='Imię', as_link=True)
    last_name = CharColumn(label='Nazwisko', as_link=True)
    registered = DateTimeColumn(label='Zarejestrowany')


class Homepage(TemplateView):

    template_name = 'homepage.html'


class PersonView(TemplateView):

    template_name = 'person.html'

    def get_context_data(self, person_id, *args, **kwargs):
        person = get_object_or_404(Person, pk=person_id)
        return {'person': person}
