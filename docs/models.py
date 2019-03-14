# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from accounts.models import add_activity
from appsettings.mixins import SeoMixin
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

# Create your models here.
def upload_location(instance, filename, *args, **kwargs):
    return "docs/images/%s" % filename

class Category(models.Model):
    name = models.CharField(max_length=120)
    icon_name = models.CharField(max_length=30)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        ordering = ['name']



class Doc(SeoMixin):
    category = models.ForeignKey(Category, null=True, blank=False)
    title = models.CharField(max_length=120)
    content = models.TextField()
    draft = models.BooleanField('Черновик', default=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created"]

    def get_absolute_url(self):
        return reverse("docs:doc_detail", kwargs={"pk":self.id})

    def get_delete_url(self):
        return reverse("docs:doc_delete", kwargs = {"pk":self.id})

    def get_update_url(self):
        return reverse("docs:doc_update", kwargs = {"pk":self.id})

    def doc_publish(self):
        self.draft = False
        self.save()

    def doc_draft(self):
        self.draft = True
        self.save()


class DocImage(models.Model):
    doc = models.ForeignKey(Doc)
    image = models.ImageField(upload_to=upload_location)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id

















