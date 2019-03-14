# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from appsettings.models import (
    CompetitionStatus,
    ExerciseCommentName,
    Unit,
    MainMuscle,
    OtherMuscle,
    ExerciseType,
    Biomech,
    Vektor,
    Equipment,
    DifficultyLevel,
    RecipeType,
    RecipeFoodType,
    RecipeAppointment,
    RecipeMode,
    RecipeCooktime,
    RecipeCookmethod,
    PRODUCT_MEAL_CHOICES,
    WorkoutOccupation,
    ModelSex
    )
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from embed_video.fields import EmbedVideoField
from uuslug import slugify
from subscriptions.templates import GENERAL_MUSCLES

# Create your models here.
def fitness_club_upload_location(instance, filename):
    return "fitnessclub/images/%s" % filename

def exercise_upload_location(instance, filename):
    ext = filename.split('.')[1]
    return "exercises/images/%s.%s" % (slugify(instance.name), ext)

def competition_upload_location(instance, filename):
    return "competition/images/%s" % filename

def product_uploads(instance, filename, *args, **kwargs):
    return 'products/%s' % filename

class Muscle(models.Model):
    name = models.CharField('Название группы мышц', max_length=50)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("options:muscle_detail", kwargs={"pk":self.pk})

    def get_delete_url(self):
        return reverse("options:muscle_delete", kwargs = {"pk":self.pk})

    def get_update_url(self):
        return reverse("options:muscle_update", kwargs = {"pk":self.pk})


class Exercise(models.Model):
    approved = models.BooleanField(default=False)
    name = models.CharField(default='', max_length=150)
    content_owner = models.ForeignKey('accounts.Trainer', on_delete=models.SET_NULL, null=True, blank=True)
    workout_occupation = models.ForeignKey(WorkoutOccupation, null=True)
    model_sex = models.ForeignKey(ModelSex, null=True)
    main_muscle = models.ForeignKey(MainMuscle, null=True)
    other_muscle = models.ForeignKey(OtherMuscle, null=True, blank=True)
    exercise_type = models.ForeignKey(ExerciseType, null=True, blank=True)
    biomech = models.ForeignKey(Biomech, null=True, blank=True)
    vektor = models.ForeignKey(Vektor, null=True, blank=True)
    equipment = models.ForeignKey(Equipment, null=True, blank=True)
    difficulty_level = models.ForeignKey(DifficultyLevel, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    video = EmbedVideoField(null=True, blank=True)
    short_video = EmbedVideoField()
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)


    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return reverse("options:exercise_detail", kwargs={"pk":self.pk})

    def get_update_url(self):
        return reverse("options:exercise_update", kwargs = {"pk":self.pk})

    def get_delete_url(self):
        return reverse("options:exercise_delete", kwargs = {"pk":self.pk})

    def get_video_thumb(self):
        try:
            video_code = self.short_video.split('?v=')[1]
        except:
            video_code = self.short_video.split('/')[-1]
        return 'https://img.youtube.com/vi/{0}/2.jpg'.format(video_code)


class FitnessClub(models.Model):
    name = models.CharField(max_length=50)
    content = models.TextField(blank=True, null=True)
    video_url = models.URLField(max_length=250, blank=True, null=True)
    private = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return reverse("options:fitnessclub_detail", kwargs={"pk":self.pk})

    def get_update_url(self):
        return reverse("options:fitnessclub_update", kwargs = {"pk":self.pk})

    def get_delete_url(self):
        return reverse("options:fitnessclub_delete", kwargs = {"pk":self.pk})

class FitnessClubImage(models.Model):
    fitnessclub = models.ForeignKey(FitnessClub, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to=fitness_club_upload_location, blank=True, null=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id


class Kbzu1Portion(models.Model):
    weight = models.FloatField(default=0, blank=True, null=True)
    protein = models.FloatField(default=0, blank=False, null=True)
    fat = models.FloatField(default=0, blank=False, null=True)
    carbohydrate = models.FloatField(default=0, blank=False, null=True)
    kkal = models.FloatField(default=0, blank=False, null=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id

class Kbzu100g(models.Model):
    weight = models.FloatField(default=0, blank=True, null=True)
    protein = models.FloatField(default=0, blank=False, null=True)
    fat = models.FloatField(default=0, blank=False, null=True)
    carbohydrate = models.FloatField(default=0, blank=False, null=True)
    kkal = models.FloatField(default=0, blank=False, null=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id


class Recipe(models.Model):
    portion_number = models.IntegerField(default=0, blank=True, null=True)
    recipe_type = models.ManyToManyField(RecipeType, blank=True)
    recipe_appointment = models.ManyToManyField(RecipeAppointment, blank=True)
    recipe_food_type = models.ManyToManyField(RecipeFoodType, blank=True)
    recipe_mode = models.ManyToManyField(RecipeMode, blank=True)
    recipe_time = models.ManyToManyField(RecipeCooktime, blank=True)
    recipe_method = models.ManyToManyField(RecipeCookmethod, blank=True)
    ingridients = models.TextField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id


class Product(models.Model):
    image = models.ImageField(upload_to=product_uploads, default='product_default_img.jpg')
    name = models.CharField(max_length=250, blank=False, null=True)
    product_meal = models.CharField('Тип продукта', max_length=1, choices=PRODUCT_MEAL_CHOICES)
    kbzu_100g = models.ForeignKey(Kbzu100g, blank=True, null=True)
    kbzu_1portion = models.ForeignKey(Kbzu1Portion, null=True, blank=True)
    recipe = models.ForeignKey(Recipe, null=True, blank=True)
    category = models.CharField(max_length=250, blank=False, null=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    def get_update_url(self):
        return reverse("options:product_update", kwargs = {"pk":self.pk})

    def get_delete_url(self):
        return reverse("options:product_delete", kwargs = {"pk":self.pk})

    def recipe_appointment(self):
        if self.recipe:
            return self.recipe.recipe_appointment.name
        return

    def recipe_food_type(self):
        if self.recipe:
            return self.recipe.recipe_food_type.name
        return


class Competition(models.Model):
    name = models.CharField(max_length=250)
    content = models.TextField()
    image = models.ImageField(upload_to=competition_upload_location)
    video = models.URLField(max_length=250, blank=True, null=True)
    start_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    finish_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    status = models.ForeignKey(CompetitionStatus, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return reverse("options:competition_detail", kwargs={"pk":self.pk})

    def get_update_url(self):
        return reverse("options:competition_update", kwargs = {"pk":self.pk})

    def get_delete_url(self):
        return reverse("options:competition_delete", kwargs = {"pk":self.pk})






