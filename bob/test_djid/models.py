# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
    company = models.ForeignKey('Company')
    score = models.IntegerField(null=True)

    def get_absolute_url(self):
        return reverse('person_view', kwargs={'person_id': self.pk})


class Company(models.Model):
    """Test company object."""
    name = models.CharField(max_length=64)
    phone = models.CharField(max_length=64)

    def get_absolute_url(self):
        return reverse('company_view', kwargs={'company_id': self.pk})

    def __str__(self):
        return self.name
