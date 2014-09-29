from django.conf.urls import patterns, include, url

from bob.djid import Djid
from bob.test_djid.views import Homepage, PersonView

urlpatterns = patterns(
    '',
    url(r'^$', Homepage.as_view()),
    url(
        r'^person/(?P<person_id>[0-9]+)/$',
        PersonView.as_view(),
        name='person_view',
    ),
    url(r'^djid/(?P<djid_id>[A-Za-z0-9]+)/$', Djid.dispatcher),
)
