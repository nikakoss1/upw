# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

#############################################################################################################################
## ACTIVITY

class Activity(models.Model):
    client = models.ForeignKey('accounts.Client', blank=False, null=True)
    client_create = models.BooleanField(default=False)
    progress = models.ForeignKey('accounts.Progress', on_delete=models.SET_NULL, blank=True, null=True)
    workout = models.ForeignKey('accounts.Workout', on_delete=models.SET_NULL, blank=True, null=True)
    workoutcomment = models.ForeignKey('accounts.WorkoutComment', on_delete=models.SET_NULL, blank=True, null=True)
    foodprogram = models.ForeignKey('accounts.FoodProgram', on_delete=models.SET_NULL, blank=True, null=True)
    article = models.ForeignKey('articles.Article', on_delete=models.SET_NULL, blank=True, null=True)
    content = models.CharField(max_length=120, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.created