from django.conf.urls import  url
from options.api.views import ProductListAPIView, ProductRetrieveAPIView, ExerciseListAPIView, ExerciseRetrieveAPIView

urlpatterns = [
    url(r'^products/$', ProductListAPIView.as_view(), name='product_list_api'),
    url(r'^products/(?P<pk>\d+)/$', ProductRetrieveAPIView.as_view(), name='product_detail'),
    url(r'^exercises/$', ExerciseListAPIView.as_view(), name='exercise_list_api'),
    url(r'^exercises/(?P<pk>\d+)/$', ExerciseRetrieveAPIView.as_view(), name='exercise_detail'),


]