from django.conf.urls import  url
from .views import (
        ArticleCreateView,
        ArticleDeleteView,
        ArticleDetailView,
        ArticleListView,
        ArticleUpdateView,
        article_publish,
        article_draft,
        )

urlpatterns = [
    url(r'^articles/$', ArticleListView.as_view(), name="article_list"),
    url(r'^articles/add/$', ArticleCreateView.as_view(), name="article_create"),
    url(r'^articles/(?P<slug>[\w-]+)/$', ArticleDetailView.as_view(), name='article_detail'),
    url(r'^articles/(?P<slug>[\w-]+)/publish/$', article_publish, name='article_publish'),
    url(r'^articles/(?P<slug>[\w-]+)/draft/$', article_draft, name='article_draft'),
    url(r'^articles/(?P<slug>[\w-]+)/update/$', ArticleUpdateView.as_view(), name='article_update'),
    url(r'^articles/(?P<slug>[\w-]+)/delete/$', ArticleDeleteView.as_view(), name='article_delete'),

]
