from django.conf.urls import  url
from .views import (
        DocCreateView,
        DocDeleteView,
        DocDetailView,
        DocListView,
        DocUpdateView,
        doc_publish,
        doc_draft,
        )

urlpatterns = [
    url(r'^$', DocListView.as_view(), name="doc_list"),
    url(r'^add/$', DocCreateView.as_view(), name="doc_create"),
    url(r'^(?P<pk>\d+)/$', DocDetailView.as_view(), name='doc_detail'),
    url(r'^(?P<pk>\d+)/publish/$', doc_publish, name='doc_publish'),
    url(r'^(?P<pk>\d+)/draft/$', doc_draft, name='doc_draft'),
    url(r'^(?P<pk>\d+)/update/$', DocUpdateView.as_view(), name='doc_update'),
    url(r'^(?P<pk>\d+)/delete/$', DocDeleteView.as_view(), name='doc_delete'),

]
