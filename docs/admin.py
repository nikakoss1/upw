# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Doc, Category

admin.site.register(Category)
admin.site.register(Doc)
