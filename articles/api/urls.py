from django.conf.urls import  url
from articles.api.views import ArticleListAPIView, ArticleRetrieveAPIView, ArticleCreateAPIView, ArticleImageRetrieveAPIView, ArticleUpdateAPIView, ArticleImageCreateAPIView, ArticleImageUpdateAPIView, LikeCreateAPIView, CommentCreateAPIView

urlpatterns = [
    url(r'^$', ArticleListAPIView.as_view(), name='article_list_api'),
    url(r'^create/$', ArticleCreateAPIView.as_view(), name='article_create_api'),
    url(r'^(?P<slug>[\w-]+)/$', ArticleRetrieveAPIView.as_view(), name='article_detail_api'),
    url(r'^(?P<slug>[\w-]+)/update/$', ArticleUpdateAPIView.as_view(), name='article_update_api'),
    url(r'^articleimages/(?P<pk>\d+)/$', ArticleImageRetrieveAPIView.as_view(), name='articleimage_detail_api'),
    url(r'^articleimages/(?P<pk>\d+)/update/$', ArticleImageRetrieveAPIView.as_view(), name='articleimage_update_api'),
    url(r'^articleimages/create/$', ArticleImageCreateAPIView.as_view(), name='articleimage_create_api'),
    url(r'^likes/create/$', LikeCreateAPIView.as_view(), name='like_create_api'),
    url(r'^comments/create/$', CommentCreateAPIView.as_view(), name='comment_create_api'),
]