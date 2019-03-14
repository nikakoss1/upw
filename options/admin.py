# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import  Muscle, Exercise, Competition, FitnessClub, FitnessClubImage, Product, Recipe, Kbzu1Portion, Kbzu100g
# Register your models here.


# class MuscleAdmin(admin.ModelAdmin):
#     class Meta:
#         model = Muscle
# admin.site.register(Muscle, MuscleAdmin)

class CompetitionAdmin(admin.ModelAdmin):
    class Meta:
        model = Competition
admin.site.register(Competition, CompetitionAdmin)

class FitnessClubAdmin(admin.ModelAdmin):
    class Meta:
        model = FitnessClub

class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    search_fields = ('id',)

class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('id','name', 'recipe_appointment', 'recipe_food_type')
    search_fields = ('name', )

class ExerciseAdmin(admin.ModelAdmin):
    model = Exercise
    list_display = ('id','name', 'workout_occupation', 'model_sex','main_muscle','short_video')
    search_fields = ('name', )

admin.site.register(FitnessClub, FitnessClubAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(FitnessClubImage)
admin.site.register(Product, ProductAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Kbzu100g)
admin.site.register(Kbzu1Portion)




