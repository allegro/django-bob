# vim: set fileencoding=utf-8
from bob.djid import Djid
from bob.djid.column import CharColumn, DateTimeColumn
from bob.test_djid.models import Person

from django.views.generic import TemplateView

class PersonsGrid(Djid):

    class Meta:
        djid_id = 'persons'

    query_set = Person.objects.all()

    first_name = CharColumn(label='Imię')
    last_name = CharColumn(label='Nazwisko')
    registered = DateTimeColumn(label='Zarejestrowany')


class Homepage(TemplateView):

    template_name = 'homepage.html'
