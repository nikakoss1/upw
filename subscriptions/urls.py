from django.conf.urls import  url
from .views import (
    program_feature_add,
    program_feature_delete,
    program_price_add,
    program_price_delete,
    ProgramCreateView,
    ProgramDetailView,
    ProgramListView,
    ProgramUpdateView,
    ProgramDeleteView,
    program_workout_delete,
    WorkoutTemplateCreateView,
    WorkoutTemplateDeleteView,
    WorkoutTemplateUpdateView,
    WsetTemplateCreateView,
    training_template_create,
    training_template_delete,
    CustomWorkoutUpdateView,
    CustomWorkoutDeleteView,
    CustomWsetCreateView,
    CustomWsetUpdateView,
    CustomWorkoutCreateView,
    custom_training_create,
    custom_training_delete,
    FoodProgramTemplateCreateView,
    FoodProgramTemplateDetailView,
    FoodProgramTemplateUpdateView,
    FoodProgramTemplateDeleteView,
    food_template_create,
    food_template_delete,
        )

urlpatterns = [
    ## PROGRAMS
    url(r'^programs/$', ProgramListView.as_view(), name="program_list"),
    url(r'^programs/create/$', ProgramCreateView.as_view(), name="program_create"),
    url(r'^programs/(?P<pk>\d+)/detail/$', ProgramDetailView.as_view(), name="program_detail"),
    url(r'^programs/(?P<pk>\d+)/update/$', ProgramUpdateView.as_view(), name="program_update"),
    url(r'^programs/(?P<pk>\d+)/delete/$', ProgramDeleteView.as_view(), name="program_delete"),
    url(r'^workout-delete/$', program_workout_delete, name="program_workout_delete"),
    url(r'^programs/(?P<pk>\d+)/update/price-add$', program_price_add, name="program_price_add"),
    url(r'^programs/(?P<pk>\d+)/update/price-delete$', program_price_delete, name="program_price_delete"),
    url(r'^programs/(?P<pk>\d+)/update/feature-add$', program_feature_add, name="program_feature_add"),
    url(r'^programs/(?P<pk>\d+)/update/feature-delete$', program_feature_delete, name="program_feature_delete"),

    ## WORKOUT TEMPLATES
    url(r'^programs/(?P<pk>\d+)/update/workout-templates/create/$', WorkoutTemplateCreateView.as_view(), name="workout_template_create"),
    url(r'^programs/(?P<pk>\d+)/update/workout-templates/(?P<id>\d+)/update/$', WorkoutTemplateUpdateView.as_view(), name="workout_template_update"),
    url(r'^programs/(?P<pk>\d+)/update/workout-templates/(?P<id>\d+)/delete/$', WorkoutTemplateDeleteView.as_view(), name="workout_template_delete"),
    url(r'^workout-templates/(?P<pk>\d+)/update/wset-templates/create/$', WsetTemplateCreateView.as_view(), name="wset_template_create"),
    url(r'^wset-templates/training-template-create/$', training_template_create, name="training_template_create"),
    url(r'^wset-templates/training-template-delete/$', training_template_delete, name="training_template_delete"),

    ## CUSTOM WORKOUT TEMPLATES
    url(r'^programs/(?P<pk>\d+)/update/custom-workout/create/$', CustomWorkoutCreateView.as_view(), name="custom_workout_create"),
    url(r'^custom-workout/(?P<pk>\d+)/update/$', CustomWorkoutUpdateView.as_view(), name="custom_workout_update"),
    url(r'^custom-workout/(?P<pk>\d+)/delete/$', CustomWorkoutDeleteView.as_view(), name="custom_workout_delete"),
    url(r'^custom-workout/(?P<pk>\d+)/update/custom-wset/create/$', CustomWsetCreateView.as_view(), name="custom_wset_create"),
    url(r'^custom-workout/(?P<pk>\d+)/update/custom-wset/(?P<sk>\d+)/update/$', CustomWsetUpdateView.as_view(), name="custom_wset_update"),
    url(r'^custom-wset-templates/custom-training-create/$', custom_training_create, name="custom_training_create"),
    url(r'^custom-wset-templates/custom-training-delete/$', custom_training_delete, name="custom_training_delete"),

    ## FOODPROGRAM TEMPLATES
    url(r'^programs/(?P<pk>\d+)/update/foodprogram-templates/create/$', FoodProgramTemplateCreateView.as_view(), name="foodprogram_template_create"),
    url(r'^programs/(?P<pk>\d+)/update/foodprogram-templates/(?P<id>\d+)/detail/$', FoodProgramTemplateDetailView.as_view(), name="foodprogram_template_detail"),
    url(r'^programs/(?P<pk>\d+)/update/foodprogram-templates/(?P<id>\d+)/update/$', FoodProgramTemplateUpdateView.as_view(), name="foodprogram_template_update"),
    url(r'^programs/(?P<pk>\d+)/update/foodprogram-templates/(?P<id>\d+)/delete/$', FoodProgramTemplateDeleteView.as_view(), name="foodprogram_template_delete"),
    url(r'^programs/food-template-create/$', food_template_create, name="food_template_create"),
    url(r'^programs/food-template-delete/$', food_template_delete, name="food_template_delete"),
]







