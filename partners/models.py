# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from accounts.models import Trainer
from django.contrib.auth.models import User
from appsettings.models import CatalogOrderTime


class Partner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trainer = models.OneToOneField(Trainer, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    promocode = models.CharField(max_length=50, null=True, blank=False)
    discount = models.IntegerField('Постоянная скидка на каталог от партнера в %', default=0, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.user.get_full_name()

    def get_delete_url(self):
        return reverse("partners:partner_delete", kwargs = {"pk":self.pk})

    def get_update_url(self):
        return reverse("partners:partner_update", kwargs={"pk":self.pk})

    def get_detail_url(self):
        return reverse("partners:partner_detail", kwargs={"pk":self.pk})

    def get_promo_generate_url(self):
        return reverse("partners:promo_generate", kwargs={"pk":self.pk})


class PromoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(free=True)


class Promo(models.Model):
    free = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    partner = models.ForeignKey(Partner)
    name = models.SlugField(max_length=70, unique=True, null=True, blank=True)
    catalog_order_time = models.ForeignKey(CatalogOrderTime, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    objects = models.Manager()
    free_objects = PromoManager()

    def __str__(self):
        return "%s: %s" % (self.partner, self.name)

    def get_delete_url(self):
        return reverse("partners:promo_delete", kwargs = {"pk":self.pk})

    def get_update_url(self):
        return reverse("partners:promo_update", kwargs={"pk":self.pk})













