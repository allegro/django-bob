from django.core.urlresolvers import reverse
from django.db import models


class Person(models.Model):
    """Test person object reflecting the data from 
    http://www.briandunning.com/sample-data/"""
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    address = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    county = models.CharField(max_length=64)
    postal = models.CharField(max_length=64)
    phone = models.CharField(max_length=64)
    email = models.CharField(max_length=64)
    web = models.CharField(max_length=64)
    registered = models.DateTimeField()
    company = models.ForeignKey('Company', null=True)

    def get_absolute_url(self):
        return reverse('person_view', kwargs={'person_id': self.pk})


class Company(models.Model):
    """Test company object."""
    name = models.CharField(max_length=64)
    phone = models.CharField(max_length=64)
