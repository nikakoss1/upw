from django.conf.urls import  url
from .views import (
    MuscleCreateView,
    MuscleDeleteView,
    MuscleUpdateView,
    MuscleDetailView,
    ExerciseListView,
    ExerciseCreateView,
    ExerciseDetailView,
    ExerciseDeleteView,
    ExerciseUpdateView,
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    )
from accounts.views import json_personal_exercise_list, json_exercisecomment_detail, json_product_list, filter_exercise_list
from subscriptions.views import json_template_exercise_list

urlpatterns = [
    url(r'^muscles/$', MuscleCreateView.as_view(), name="muscle_create"),
    url(r'^muscles/(?P<pk>\d+)/$', MuscleDetailView.as_view(), name='muscle_detail'),
    url(r'^muscles/(?P<pk>\d+)/update/$', MuscleUpdateView.as_view(), name='muscle_update'),
    url(r'^muscles/(?P<pk>\d+)/delete/$', MuscleDeleteView.as_view(), name='muscle_delete'),
    url(r'^exercises/$', ExerciseListView.as_view(), name="exercise_list"),
    url(r'^exercises/json/$', json_personal_exercise_list, name="json_personal_exercise_list"),
    url(r'^filter-exercises/json/$', filter_exercise_list, name="filter_exercise_list"),
    url(r'^products/json/$', json_product_list, name="json_product_list"),
    url(r'^exercises/template-json/$', json_template_exercise_list, name="json_template_exercise_list"),
    url(r'^exercises/comments/json/$', json_exercisecomment_detail, name="json_exercisecomment_detail"),
    url(r'^exercises/add/$', ExerciseCreateView.as_view(), name="exercise_create"),
    url(r'^exercises/(?P<pk>\d+)/$', ExerciseDetailView.as_view(), name='exercise_detail'),
    url(r'^exercises/(?P<pk>\d+)/update/$', ExerciseUpdateView.as_view(), name='exercise_update'),
    url(r'^exercises/(?P<pk>\d+)/delete/$', ExerciseDeleteView.as_view(), name='exercise_delete'),
    url(r'^products/$', ProductListView.as_view(), name="product_list"),
    url(r'^products/add/$', ProductCreateView.as_view(), name="product_create"),
    url(r'^products/(?P<pk>\d+)/update/$', ProductUpdateView.as_view(), name='product_update'),
    url(r'^products/(?P<pk>\d+)/delete/$', ProductDeleteView.as_view(), name='product_delete'),
]
