# -*- coding: utf-8 -*-
from .models import AppSettings, CompetitionStatus, Unit, SettingsDay, SettingsTime, ExerciseCommentName, SettingsRestTime, WorkoutCommentName, MainMuscle, OtherMuscle, ExerciseType, RecipeType, CatalogOrderTime, PersonalPPBuyPackage, PersonalWorkoutBuyPackage, WorkoutOccupation, ModelSex, WelcomeMessage
from django.contrib import admin
from preferences.admin import PreferencesAdmin
# Register your models here.
admin.site.register(AppSettings, PreferencesAdmin)
admin.site.register(CompetitionStatus)
admin.site.register(ExerciseCommentName)
admin.site.register(SettingsDay)
admin.site.register(SettingsRestTime)
admin.site.register(SettingsTime)
admin.site.register(Unit)
admin.site.register(WorkoutCommentName)
admin.site.register(MainMuscle)
admin.site.register(OtherMuscle)
admin.site.register(ExerciseType)
admin.site.register(RecipeType)
admin.site.register(CatalogOrderTime)
admin.site.register(PersonalPPBuyPackage)
admin.site.register(PersonalWorkoutBuyPackage)
admin.site.register(WorkoutOccupation)
admin.site.register(ModelSex)
admin.site.register(WelcomeMessage)



