# -*- coding: utf-8 -*-
from appsettings.mixins import (
    HasGroupPermissionMixin,
    )
from django.views.generic.list import ListView
from .models import DailyStat, DownloadReferer


class DailyStatListView(HasGroupPermissionMixin, ListView):
    model = DailyStat

    def get_context_data(self, **kwargs):
        context = super(DailyStatListView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners', 'administration']
        self.has_multiple_group(*groups)
        queryset = self.get_queryset()
        context['title'] = 'Ежедневная статистика'
        return context


class DownloadRefererListView(HasGroupPermissionMixin, ListView):
    model = DownloadReferer

    def get_context_data(self, **kwargs):
        context = super(DownloadRefererListView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners', 'administration']
        self.has_multiple_group(*groups)
        queryset = self.get_queryset()
        context['title'] = 'Статистика скачиваний'
        return context

