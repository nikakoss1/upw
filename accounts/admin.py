# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import (
    Client,
    Day,
    ExerciseComment,
    Food,
    FoodProgram,
    # GeneralNutrimentProfile,
    # GeneralWorkoutProfile,
    LeadUser,
    Message,
    Note,
    PersonalNutrimentProfile,
    PersonalWorkoutProfile,
    Progress,
    Time,
    Trainer,
    Training,
    Workout,
    WorkoutComment,
    Wset,
    )
# # Register your models here.

admin.site.register(Client)
admin.site.register(Trainer)
admin.site.register(Progress)
admin.site.register(Message)
admin.site.register(Food)
admin.site.register(FoodProgram)
admin.site.register(Day)
admin.site.register(Time)
admin.site.register(Workout)
admin.site.register(Training)
admin.site.register(Wset)
admin.site.register(LeadUser)
admin.site.register(ExerciseComment)
admin.site.register(WorkoutComment)
admin.site.register(Note)
# admin.site.register(GeneralNutrimentProfile)
# admin.site.register(GeneralWorkoutProfile)
admin.site.register(PersonalNutrimentProfile)
admin.site.register(PersonalWorkoutProfile)



