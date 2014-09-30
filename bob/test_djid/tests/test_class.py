# vim: set fileencoding=utf-8
"""Tests for Djid class."""

import unittest

from bob.djid import Djid
from bob.djid.column import CharColumn, DateTimeColumn
from bob.test_djid.models import Person


class TestCustomClass(unittest.TestCase):
    """Test for a class with all custom columns."""

    def setUp(self):
        class PersonsGrid(Djid):

            class Meta:
                djid_id = 'persons'
                query_set = Person.objects.all()

            first_name = CharColumn(label='Imię')
            last_name = CharColumn(label='Nazwisko')
            registered = DateTimeColumn(label='Zarejestrowany')
        self.PersonsGrid = PersonsGrid

    def test_columns(self):
        """The grid has correct columns in correct order."""

        self.assertListEqual(
            list(self.PersonsGrid._meta.column_dict.keys()),
            ['first_name', 'last_name', 'registered']
        )


class TestReflectedClass(unittest.TestCase):
    """Test for a class that has its columns reflected."""

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
        self.PersonsGrid = PersonsGrid

    def test_columns(self):
        """The grid has correct columns in correct order."""

        self.assertListEqual(
            list(self.PersonsGrid._meta.column_dict.keys()),
            ['first_name', 'last_name', 'registered']
        )