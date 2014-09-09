# Create your views here.
from bob.djid import Djid
from bob.djid.column import CharColumn
from bob.test_djid.models import Person

class PersonsGrid(Djid):

    query_set = Person.objects.all()

    first_name = CharColumn()
    last_name = CharColumn()
