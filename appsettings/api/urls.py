from django.conf.urls import  url
from appsettings.api.views import (AppsettingsRetriveView)

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', AppsettingsRetriveView.as_view(), name='appsettings_api'),
    ]
