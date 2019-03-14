# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Status, Bloger

admin.site.register(Status)
admin.site.register(Bloger)

