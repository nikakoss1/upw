# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from accounts.models import (
    SEX,
    LEVELS,
    )
from accounts.workout_models import (
    Training,
    Workout,
    Wset,
    )
from appsettings.models import (
    MainMuscle,
    OtherMuscle,
    ExerciseType,
    SettingsRestTime,
    PROGRAM_TYPE_CHOICES,
    SettingsTime,
    SettingsDay,
    Biomech,
    Vektor,
    DifficultyLevel,
    Equipment,
    WorkoutOccupation,
    PROGRAM_LOCATION,
    PROGRAM_LEVEL,
    )
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from options.models import (
    Muscle,
    Exercise,
    Product,
    )

#############################################################################################################################
## HELP FUNCS

def program_uploads(instance, filename, *args, **kwargs):
    return 'programs/%s' % filename

#############################################################################################################################
## WORKOUT PROGRAMS

class Category(models.Model):
    parent_category = models.ForeignKey('self', null=True, blank=True)
    name = models.CharField(max_length=255)
    img = models.ImageField(upload_to=program_uploads, default='programs/program_bg.png')
    desc = models.TextField()
    rating = models.PositiveIntegerField(default=1)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return reverse("members:category_detail", kwargs = {"pk":self.id})

    def get_member_food_absolute_url(self):
        return reverse("members:food_category_detail", kwargs = {"pk":self.id})


class Program(models.Model):
    is_active = models.BooleanField(default=False)
    category = models.ManyToManyField(Category, blank=False)
    demo = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True, blank=False)
    short_desc = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    img = models.ImageField(upload_to=program_uploads, default='programs/program_bg.png')
    video = models.URLField(max_length=250, blank=True, null=True)
    program_type = models.CharField(max_length=2, choices=PROGRAM_TYPE_CHOICES, null=True, blank=False)
    program_location = models.CharField(max_length=25, choices=PROGRAM_LOCATION, null=True, blank=False)
    program_level = models.CharField(max_length=25, choices=PROGRAM_LEVEL, null=True, blank=False)
    content_owner = models.ForeignKey('accounts.Trainer', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveIntegerField(default=1)
    recommend = models.BooleanField(default=False)
    to_all = models.BooleanField(default=False)
    daily = models.BooleanField(default=False)
    chargeable = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name

    def get_update_url(self):
        return reverse("subscriptions:program_update", kwargs = {"pk":self.id})

    def get_detail_url(self):
        if self.program_type == 'WP' or self.program_type == 'FP' or self.program_type == 'FG':
            return None
        else:
            return reverse("subscriptions:program_detail", kwargs = {"pk":self.id})

    def get_memberzone_detail_url(self):
        if self.program_type == 'WC' or self.program_type == 'WG':
            return reverse("members:member_program_detail", kwargs = {"pk":self.id})
        return None

    def get_memberzone_food_detail_url(self):
        if self.program_type == 'FG':
            return reverse("members:member_foodprogram_detail", kwargs = {"pk":self.id})
        return None


    def get_delete_url(self):
        return reverse("subscriptions:program_delete", kwargs = {"pk":self.id})

    def get_program_workout_delete_url(self):
            return reverse("subscriptions:program_workout_delete")

    def get_program_type(self):
        if self.program_type == 'WP':
            return '{0}'.format(PROGRAM_TYPE_CHOICES[0][1])
        elif self.program_type == 'FP':
            return '{0}'.format(PROGRAM_TYPE_CHOICES[1][1])
        elif self.program_type == 'WG':
            return '{0}'.format(PROGRAM_TYPE_CHOICES[2][1])
        elif self.program_type == 'WC':
            return '{0}'.format(PROGRAM_TYPE_CHOICES[3][1])
        elif self.program_type == 'FG':
            return '{0}'.format(PROGRAM_TYPE_CHOICES[4][1])
        elif self.program_type == 'MT':
            return '{0}'.format(PROGRAM_TYPE_CHOICES[5][1])
        elif self.program_type == 'EX':
            return '{0}'.format(PROGRAM_TYPE_CHOICES[6][1])

    def price_type(self):
        if self.chargeable:
            return '{0}'.format('Да')
        else:
            return '{0}'.format('Нет')

    def get_number_exercises(self):
        lst = []
        for workout in self.workout_set.all():
            for wset in workout.wset_set.all():
                lst.append(wset.training_set.all().count())
        return sum(lst)

    def get_number_workouts(self):
        return self.workout_set.all().count()


class Feature(models.Model):
    program = models.ForeignKey(Program, null=True, blank=False)
    name = models.CharField(max_length=255, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return "%s" % self.name

# class Price(models.Model):
#     program = models.ForeignKey(Program, null=True, blank=False)
#     name = models.CharField(max_length=255, null=True, blank=False)
#     price = models.PositiveIntegerField(default=0)
#     number = models.PositiveIntegerField(default=1, blank=True)
#     created = models.DateField(auto_now_add=True, auto_now=False)
#     updated = models.DateTimeField(auto_now_add=False, auto_now=True)

#     class Meta:
#         ordering = ['-created']

#     def __str__(self):
#         return "%s" % self.name


class Favourite(models.Model):
    program = models.ForeignKey(Program)
    client = models.ForeignKey('accounts.Client')
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['program']

    def __str__(self):
        return "%s | %s" % (self.program, self.client)


#############################################################################################################################
## WORKOUT TEMPLATES

class WorkoutTemplate(models.Model):
    program = models.ForeignKey(Program, null=True, blank=False)
    number = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=255, null=True, blank=False)
    sex = models.CharField('Пол', max_length=1, choices=SEX, null=True, blank=True)
    training_level = models.CharField('Уровень физ подготовки', max_length=4, choices=LEVELS, null=True, blank=True)
    rest = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return "%s:%s" % (self.name, self.created)

    def get_update_url(self):
        return reverse("subscriptions:workout_template_update", kwargs = {'pk':self.program.id, "id":self.id})

    def get_detail_url(self):
        return reverse("subscriptions:workout_template_detail", kwargs = {'pk':self.program.id, "id":self.id})

    def get_delete_url(self):
        return reverse("subscriptions:workout_template_delete", kwargs = {'pk':self.program.id, "id":self.id})

    def sex_value(self):
        if self.sex == None:
            return ''
        if self.sex == 'M':
            return '{0}'.format(SEX[0][1])
        elif self.sex == 'F':
            return '{0}'.format(SEX[1][1])

    def level_value(self):
        if self.training_level == None:
            return ''
        if self.training_level == 'N':
            return '{0}'.format(LEVELS[0][1])
        elif self.training_level == 'M':
            return '{0}'.format(LEVELS[1][1])
        elif self.training_level == 'A':
            return '{0}'.format(LEVELS[2][1])
        elif self.training_level == 'P':
            return '{0}'.format(LEVELS[3][1])


@receiver(post_delete, sender=WorkoutTemplate)
def workout_template_post_delete(sender, instance, **kwargs):
    try:
        program_obj = instance.program
    except:
        return
    program_obj.is_active = False
    program_obj.save()
    return


class WsetTemplate(models.Model):
    workout_template = models.ForeignKey(WorkoutTemplate)
    number = models.IntegerField(null=True, blank=True)
    approach_number = models.PositiveIntegerField(default=1)
    rest_time = models.ForeignKey(SettingsRestTime, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s | %s' % (self.workout_template, self.number)

    class Meta:
        ordering = ['number']


class TrainingTemplate(models.Model):
    workout_template = models.ForeignKey(WorkoutTemplate)
    workout_occupation = models.ForeignKey(WorkoutOccupation, null=True, blank=True)
    wset_template = models.ForeignKey(WsetTemplate)
    main_muscle = models.ForeignKey(MainMuscle, null=True, blank=True)
    other_muscle = models.ForeignKey(OtherMuscle, null=True, blank=True)
    exercise_type = models.ForeignKey(ExerciseType, null=True, blank=True)
    biomech = models.ForeignKey(Biomech, null=True, blank=True)
    vektor = models.ForeignKey(Vektor, null=True, blank=True)
    equipment = models.ForeignKey(Equipment, null=True, blank=True)
    difficulty_level = models.ForeignKey(DifficultyLevel, null=True, blank=True)
    repetition = models.PositiveIntegerField(default=12)
    rest_time = models.ForeignKey(SettingsRestTime, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s:%s" % (self.workout_template, self.wset_template)


# #############################################################################################################################
# ## FOODPROGRAM TEMPLATES

class FoodProgramTemplate(models.Model):
    program = models.ForeignKey(Program, null=True, blank=False)
    number = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(max_length=255, null=True, blank=True)
    kf = models.PositiveIntegerField(default=1, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return "%s:%s" % (self.name, self.created)

    def get_detail_url(self):
        return reverse('subscriptions:foodprogram_template_detail', kwargs={'pk':self.program.id, 'id':self.id})

    def get_update_url(self):
        return reverse('subscriptions:foodprogram_template_update', kwargs={'pk':self.program.id, 'id':self.id})

    def get_delete_url(self):
        return reverse('subscriptions:foodprogram_template_delete', kwargs={'pk':self.program.id, 'id':self.id})


class DayTemplate(models.Model):
    foodprogram_template = models.ForeignKey(FoodProgramTemplate, null=True, blank=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    sorting = models.IntegerField(null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        ordering = ['sorting']


class TimeTemplate(models.Model):
    settingstime = models.ForeignKey(SettingsTime, null=True, blank=False)
    day_template = models.ForeignKey(DayTemplate, null=True, blank=False)
    weight = models.FloatField(default=0, blank=False, null=True)
    kkal = models.FloatField(default=0, blank=False, null=True)
    protein = models.FloatField(default=0, blank=False, null=True)
    fat = models.FloatField(default=0, blank=False, null=True)
    carbohydrate = models.FloatField(default=0, blank=False, null=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.settingstime

    class Meta:
        ordering = ['settingstime']


class FoodTemplate(models.Model):
    foodprogram_template = models.ForeignKey(FoodProgramTemplate, null=True, blank=False)
    day_template = models.ForeignKey(DayTemplate, null=True, blank=True)
    time_template = models.ForeignKey(TimeTemplate, null=True, blank=False)
    product = models.ForeignKey(Product, null=True, blank=False)
    product_input = models.CharField(max_length=255, null=True, blank=False)
    weight = models.FloatField(default=0, blank=False, null=True)
    kkal = models.FloatField(default=0, blank=False, null=True)
    protein = models.FloatField(default=0, blank=False, null=True)
    fat = models.FloatField(default=0, blank=False, null=True)
    carbohydrate = models.FloatField(default=0, blank=False, null=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s / %s / %s / %s" % (self.day, self.time, self.product, self.weight)

    def get_delete_url(self):
        return reverse("subscriptions:food_template_delete")


@receiver(pre_save, sender=FoodTemplate)
def time_kbzu_post_save(sender, instance, **kwargs):
    timetemplate_obj = instance.time_template
    timetemplate_obj.weight += instance.weight
    timetemplate_obj.kkal += instance.kkal
    timetemplate_obj.protein += instance.protein
    timetemplate_obj.fat += instance.fat
    timetemplate_obj.carbohydrate += instance.carbohydrate
    timetemplate_obj.save()
    return












