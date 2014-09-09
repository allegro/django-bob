from django.conf.urls import patterns, include, url

from bob.test_djid.views import PersonsGrid

urlpatterns = patterns(
    '',
    url(r'^persons_djid/', PersonsGrid.get_ajax_data),
)
