from django.conf.urls import patterns, include, url

from bob.djid import Djid
from bob.test_djid.views import DisplayDjid, PersonView, CompanyView


urlpatterns = patterns(
    '',
    url(r'^$', DisplayDjid.as_view(), {'djid': 'persons'}),
    url(r'^companies/$', DisplayDjid.as_view(), {'djid': 'companies'}),
    url(
        r'^person/(?P<person_id>[0-9]+)/$',
        PersonView.as_view(),
        name='person_view',
    ),
    url(
        r'^company/(?P<company_id>[0-9]+)/$',
        CompanyView.as_view(),
        name='company_view',
    ),
    url(r'^djid/', include(Djid.resolver())),
)
