# -*- coding: utf-8 -*-
from .utils import add_activity
from activities.models import Activity
from appsettings.models import (
    SettingsRestTime,
    SEX,
    LEVELS,
    )
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from options.models import Exercise
import requests


def is_200(video_thumb):
    r = requests.get(video_thumb)
    return r.status_code == 200

#############################################################################################################################
## WORKOUT TAB

class Workout(models.Model):
    client = models.ForeignKey('accounts.Client', null=True, blank=True)
    leaduser = models.ForeignKey('accounts.LeadUser', null=True, blank=True)
    program = models.ForeignKey('subscriptions.Program', null=True, blank=True)
    number = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=100, null=True, blank=False)
    content = models.TextField(max_length=255, null=True, blank=True)
    sex = models.CharField('Пол', max_length=1, choices=SEX, null=True, blank=True)
    training_level = models.CharField('Уровень физ подготовки', max_length=4, choices=LEVELS, null=True, blank=True)
    rest = models.BooleanField('Отдых', default=False)
    is_finished = models.BooleanField('Завершена', default=False)
    self_content = models.BooleanField(default=False)
    suggestions = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return "%s %s" % (self.name, self.date if self.date != None else self.created)

    def activity(self, content=None):
        return add_activity(client=self.client, workout=self, content=content)

    def get_member_workout_absolute_url(self):
        return reverse("members:member_workout_detail", kwargs={"pk":self.pk})

    def get_member_food_absolute_url(self):
        return reverse("members:member_food_detail", kwargs={"pk":self.pk})

    def get_custom_workout_update_url(self):
        return reverse("subscriptions:custom_workout_update", kwargs={ "pk":self.pk })

    def get_custom_workout_delete_url(self):
        return reverse("subscriptions:custom_workout_delete", kwargs={"pk":self.pk })

    def get_name(self):
        if self.name is None:
            return 'Тренировка от {0}'.format(self.created)
        else:
            return self.name

    def get_content(self):
        return self.content if self.content != None else ''

    def get_content_or_date(self):
        content = self.content
        if self.date != None:
            content = self.date
        return content

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

    def is_rest(self):
        return self.name == 'Отдых'


@receiver(post_save, sender=Workout)
def counter_decrease(sender, instance, **kwargs):
    if instance.client:
        if kwargs['created']:
            personal_workout_profile_obj = instance.client.personalworkoutprofile
            if personal_workout_profile_obj.workout_counter > 0:
                personal_workout_profile_obj.workout_counter = personal_workout_profile_obj.workout_counter-1
                personal_workout_profile_obj.save()
    return

@receiver(post_delete, sender=Workout)
def workout_template_post_delete(sender, instance, **kwargs):
    try:
        program_obj = instance.program
        program_obj.is_active = False
        program_obj.save()
    except:
        return


@receiver(post_save, sender=Workout)
def workout_activity(sender, instance, **kwargs):
    if  kwargs['created']:
        if not Activity.objects.filter(workout=instance).first():
            if instance.client:
                return add_activity(client=instance.client, workout=instance, content='Добавлена новая тренировка "{}"'.format(instance.name))
    return


class Wset(models.Model):
    workout = models.ForeignKey(Workout, null=True, blank=False)
    number = models.IntegerField(null=True, blank=True)
    datainput = models.CharField(max_length=255, null=True, blank=True)
    approach_number = models.PositiveIntegerField(default=1)
    rest_time = models.ForeignKey(SettingsRestTime, null=True, blank=False)
    content = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%d' % self.id

    class Meta:
        ordering = ['number']

    def get_custom_wset_update_url(self):
        return reverse("subscriptions:custom_wset_update", kwargs={"pk":self.workout.id, "sk":self.id })


class Training(models.Model):
    workout = models.ForeignKey(Workout, null=True, blank=False)
    wset = models.ForeignKey(Wset, null=True, blank=False)
    exercise = models.ForeignKey(Exercise, null=True, blank=True)
    exercise_input = models.CharField(max_length=255, null=True, blank=True)
    content = models.CharField(max_length=500, null=True, blank=False)
    rest_time = models.ForeignKey(SettingsRestTime, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s:%s" % (self.workout, self.wset)

    class Meta:
        ordering = ['id']

    def get_delete_url(self):
        return reverse("accounts:training_delete")

    def get_image(self):
        short_video = self.exercise.short_video
        try:
            video_code = short_video.split('?v=')[1]
        except:
            video_code = short_video.split('/')[-1]
        return 'https://img.youtube.com/vi/{0}/sddefault.jpg'.format(video_code)

class ExerciseComment(models.Model):
    client = models.ForeignKey('accounts.Client', blank=True, null=True)
    workout = models.ForeignKey(Workout, blank=True, null=True)
    exercise = models.ForeignKey(Exercise, blank=True, null=True)
    name_id = models.PositiveIntegerField(default=0)
    content = models.TextField(max_length=255, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.exercise

class WorkoutComment(models.Model):
    client = models.ForeignKey('accounts.Client', blank=True, null=True)
    workout = models.ForeignKey('accounts.Workout', blank=True, null=True)
    content = models.TextField(max_length=255, null=True, blank=True)
    name_id = models.PositiveIntegerField(default=0)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.workout

@receiver(post_save, sender=WorkoutComment)
def workout_comment_activity(sender, instance, **kwargs):
    if  kwargs['created']:
        try:
            workout_comment_name_obj=WorkoutCommentName.objects.get(name_id=instance.name_id)
            add_activity(client=instance.client, workoutcomment=instance, content='Комментарий к тренировке {} от {}: {}. {}'.format(instance.workout.name, instance.workout.created, instance.content, workout_comment_name_obj.name))
        except Exception as e:
            print(e)
    return