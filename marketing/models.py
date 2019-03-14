# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from accounts.models import add_activity
from appsettings.mixins import SeoMixin
from appsettings.models import BLOGER_STATUS
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from uuslug import slugify
import itertools

class Status(models.Model):
    name = models.CharField(max_length=120)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        ordering = ['name']


class Bloger(models.Model):
    status = models.CharField(max_length=10, choices=BLOGER_STATUS)
    name = models.CharField(max_length=120)
    subs = models.IntegerField(default=0)
    content = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-subs"]

    def get_insta_url(self):
        return 'instagram://user?username={0}'.format(self.name)

    def get_status(self):
        for item in BLOGER_STATUS:
            if item[0] == self.status:
                return item[1]




















