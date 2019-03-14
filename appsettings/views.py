# -*- coding: utf-8 -*-
from django.shortcuts import render
from .forms import SubscriberForm
from django.views.generic.edit import FormView


class ComingSoon(FormView):
    template_name = 'appsettings/coming_soon.html'
    form_class = SubscriberForm
    success_url = '/coming-soon/'

    def get_context_data(self, **kwargs):
        context = super(ComingSoon, self).get_context_data(**kwargs)
        context['seo_title'] = 'Скоро открытие!'
        return context

