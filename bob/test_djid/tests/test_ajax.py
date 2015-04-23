"""Tests for ajax data."""
import json

from django.test import TestCase

from bob.test_djid.models import Person


class TestAjaxData(TestCase):

    def test_pages_sorted(self):
        """The sorted data is correctly paginated."""
        persons = Person.objects.order_by('first_name')
        person1 = persons[0]
        person21 = persons[20]
        data = json.loads(self.client.get(
            '/djid/persons/?page=1&sidx=first_name+&sord=asc'
        ).content)
        self.assertEqual(data['rows'][0]['cell'][0][1], person1.first_name)
        data = json.loads(self.client.get(
            '/djid/persons/?page=2&sidx=first_name+&sord=asc'
        ).content)
        self.assertEqual(data['rows'][0]['cell'][0][1], person21.first_name)

    def test_pages_unsorted(self):
        """The unsorted data is correctly paginated."""
        persons = Person.objects.all()
        person1 = persons[0]
        person21 = persons[20]
        data = json.loads(self.client.get(
            '/djid/persons/?page=1'
        ).content)
        self.assertEqual(data['rows'][0]['cell'][0][1], person1.first_name)
        data = json.loads(self.client.get(
            '/djid/persons/?page=2'
        ).content)
        self.assertEqual(data['rows'][0]['cell'][0][1], person21.first_name)
