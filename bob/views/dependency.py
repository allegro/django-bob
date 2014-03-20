# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View


logger = logging.getLogger(__name__)


class DependencyView(View):
    """
    Base view for dependencies ajax data providers.

    Request is checked for the presence of the master field value.
    Subclass must implement ``get_values`` method which returns dict of
    dependent fields values, e.g.:

    Fields 'sex' and 'country' depend on 'name'.

    Request:
    {
        'value': 'Andrzej'
    }

    Response:
    {
        'sex': 'man',
        'country': 'Poland'
    }
    """
    def get_values(self, value):
        """
        Should provide value/values of dependent fields.

        Returns dictionary with values for all dependent fields. If you need
        to define options, define tuple like (value, [option1, option2, ...]).

        If value is not proper returns HttpResponse class which
        will be returned.

        :param value: master field value, comes with ajax request
        :return: map of dependent field names - fields values

        Example:
        >>> value = 'Andrzej'

        Response:
        >>> {
            'sex': 'man',
            'marital_status': (1, [
                (1, 'single'), (2, 'widower'), (3, 'married')
            ])
        }
        """
        raise NotImplementedError("Subclass should implement this method.")

    def post(self, *args, **kwargs):
        try:
            value = self.request.POST['value']
        except KeyError:
            logger.debug("dependencies\tEmpty field value.")
            return HttpResponseBadRequest("Value is not provided.")

        result = self.get_values(value)

        if isinstance(result, HttpResponse):
            return result

        try:
            assert isinstance(result, dict)
            response = json.dumps(result)
        except (TypeError, AssertionError):
            logger.error(
                "dependencies\tget_values should return parseable dict."
            )
            return HttpResponse(status=500)
        return HttpResponse(response, mimetype="application/json")
