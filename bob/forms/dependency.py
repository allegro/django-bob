# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple

from django import forms

SHOW = 'SHOW'

Dependency = namedtuple('Dependency', ('slave', 'master', 'value', 'action'))

class DependencyForm():
    """Form mixin with dependency feature."""

    dependencies = []
