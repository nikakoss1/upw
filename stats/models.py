# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from accounts.models import LeadUser, Client
from datetime import timedelta, date
from memberzone.models import Order

#GLOBAL PARAMS
today = date.today()


class DailyStat(models.Model):
    lead_number = models.IntegerField('Количество лидов', default=0)
    client_number = models.IntegerField('Количество клиентов', default=0)
    trial_number = models.IntegerField('Количество триалов', default=0)
    payed_client_number = models.IntegerField('Количество мемберов', default=0)
    disabled_trial_number = models.IntegerField('Отключенных триалов', default=0)
    disabled_member_number = models.IntegerField('Отключенных мемберов', default=0)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-created']


    def __str__(self):
        return "%s" % self.id

    def new_lead_number(self):
        return LeadUser.objects.filter(created=self.created).count()

    def new_client_number(self):
        return Client.objects.filter(created=self.created).count()


class DownloadReferer(models.Model):
    name = models.CharField(max_length=120)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        ordering = ['name']











