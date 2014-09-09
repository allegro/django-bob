# Create your views here.
from bob.djid import Djid
from bob.djid.column import CharColumn
from bob.test_djid.models import Person

from django.views.generic import TemplateView

class PersonsGrid(Djid):

    class Meta:
        djid_id = 'persons'

    query_set = Person.objects.all()

    first_name = CharColumn()
    last_name = CharColumn()


class Homepage(TemplateView):

    template_name = 'homepage.html'
