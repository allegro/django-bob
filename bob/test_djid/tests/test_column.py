"""Tests for column objects."""
import unittest

from bob.djid import Djid
from bob.djid.column import DateTimeColumn
from bob.test_djid.models import Person


class TestCharColumn(unittest.TestCase):
    """Tests for ChaColumn"""

    def setUp(self):
        class PersonsGrid(Djid):
            class Meta:
                djid_id = 'persons'
                Model = Person
                query_set = Person.objects.all()
                columns = [
                    'first_name',
                    'last_name',
                    'registered',
                ]
            registered=DateTimeColumn(label='Zarejestrowany')

        self.PersonsGrid = PersonsGrid

    def test_filtered(self):
        """Filtered by default."""
        self.assertTrue(
            self.PersonsGrid._meta.column_dict['first_name'].
            get_model()['search']
        )
