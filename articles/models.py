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
    return "articles/images/%s" % filename


class Article(SeoMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=70, unique=True)
    content = models.TextField()
    draft = models.BooleanField('Черновик', default=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created"]

    def get_absolute_url(self):
        return reverse("articles:article_detail", kwargs={"slug":self.slug})

    def get_post_detail_url(self):
        return reverse("post_detail", kwargs={"slug":self.slug})

    def get_delete_url(self):
        return reverse("articles:article_delete", kwargs = {"slug":self.slug})

    def get_update_url(self):
        return reverse("articles:article_update", kwargs = {"slug":self.slug})

    # def save(self, *args, **kwargs):
    #     max_length = self._meta.get_field('slug').max_length
    #     self.slug = orig = slugify(self.title)[:max_length]
    #     for x in itertools.count(1):
    #         if not Article.objects.filter(slug=self.slug).exists():
    #             break
    #         self.slug = '%s-%d' % (orig[:max_length - len(str(x)) - 1], x)
    #     super(Article, self).save(*args, **kwargs)

    def article_publish(self):
        self.draft = False
        self.save()

    def article_draft(self):
        self.draft = True
        self.save()

    @property
    def owner(self):
        return self.user


## MEMBER ARTICLES
    def get_member_article_absolute_url(self):
        return reverse("members:member_article_detail", kwargs={"slug":self.slug})

    def get_member_article_delete_url(self):
        return reverse("members:member_article_delete", kwargs = {"slug":self.slug})

    def get_member_article_update_url(self):
        return reverse("members:member_article_update", kwargs = {"slug":self.slug})


@receiver(post_save, sender=Article)
def unique_slug(sender, instance, **kwargs):
    if kwargs.get('created', False):
        max_length = instance._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.title)[:max_length]
        for x in itertools.count(1):
            if not Article.objects.filter(slug=instance.slug).exists():
                break
            instance.slug = '%s-%d' % (orig[:max_length - len(str(x)) - 1], x)
        instance.save()
    return instance.slug


class ArticleImage(models.Model):
    article = models.ForeignKey(Article)
    image = models.ImageField(upload_to=upload_location)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id


class Like(models.Model):
    article = models.ForeignKey(Article)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id


class Comment(models.Model):
    article = models.ForeignKey(Article)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id

    class Meta:
        ordering = ["-created"]


















