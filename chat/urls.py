# from django.urls import path, re_path

from django.conf.urls import  url
from .views import ThreadView, InboxView

# app_name = 'chat'
# urlpatterns = [
#     path("", InboxView.as_view()),
#     re_path(r"^(?P<username>[\w.@+-]+)", ThreadView.as_view()),
# ]

urlpatterns = [
    url(r'^$', InboxView.as_view(), name="inbox_view"),
    url(r'^(?P<username>[\w.@+-]+)/$', ThreadView.as_view(), name="thread_view"),

]