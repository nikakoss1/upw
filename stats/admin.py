# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import DailyStat, DownloadReferer

admin.site.register(DailyStat)
admin.site.register(DownloadReferer)

