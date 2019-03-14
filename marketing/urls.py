from django.conf.urls import  url
from .views import (
        BlogerListView,
        bloger_status,
        )

urlpatterns = [
    url(r'^$', BlogerListView.as_view(), name="bloger_list"),
    url(r'^status/$', bloger_status, name='bloger_status'),

]
