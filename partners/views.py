# -*- coding: utf-8 -*-
from .forms import (
    PartnerForm,
    PromoForm,
    )
from .models import (
    Partner,
    Promo,
    )
from accounts.forms import (
    UserCreationForm,
    )
from appsettings.utils import get_redirect_url
from appsettings.mixins import (
    IsAuthenticatedPermissionMixin,
    IsClientPermissionMixin,
    IsmemberPermissionMixin,
    HasGroupPermissionMixin
    )
from appsettings.models import CatalogOrderTime
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from appsettings.utils import id_generator


##################################################################################################################
## PARTNERS

class PartnerListView(HasGroupPermissionMixin, ListView):
    model = Partner

    def get_context_data(self, **kwargs):
        context = super(PartnerListView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        context['title'] = 'Партнеры'
        context['addobject'] = reverse_lazy('partners:partner_create')
        return context

class PartnerCreateView(HasGroupPermissionMixin, CreateView):
    model = User
    form_class = UserCreationForm
    second_form_class = PartnerForm
    template_name = 'panel/includes/partners/partner_form.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('partners:partner_list')

    def form_valid(self, form):
        try:
            partner_form = PartnerForm(self.request.POST or None)
            if form.is_valid() and partner_form.is_valid():
                user = form.save()
                partner = partner_form.save(commit=False)
                partner.user_id = user.id
                partner_group = Group.objects.get(name='partners')
                partner_group.user_set.add(user)
                partner.save()
                promocode = partner_form.cleaned_data['promocode']
                promo_obj = Promo.objects.create(partner=partner, name=promocode)
        except Exception as e:
            print(e)
        return HttpResponseRedirect(self.get_success_url(self))

    def get_context_data(self, **kwargs):
        context = super(PartnerCreateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        context['partner_form'] = self.second_form_class
        context['title'] =  'Добавление партнера'
        context['parent_title'] = 'Партнеры'
        context['parent_url'] = reverse_lazy('partners:partner_list')
        return context

class PartnerDetailView(HasGroupPermissionMixin, DetailView):
    model = Partner

    def get_context_data(self, **kwargs):
        context = super(PartnerDetailView, self).get_context_data(**kwargs)
        groups = ['brandowners','main_trainer']
        self.has_multiple_group(*groups)
        obj = self.get_object()

        context['title'] =  'Профиль партнера {0}'.format(obj)
        context['parent_title'] = 'Партнеры'
        administration = ['brandowners',]
        if self.request.user.groups.filter(name__in=administration).exists():
            context['addobject'] = reverse_lazy('partners:promo_generate', kwargs={'pk':self.kwargs['pk']})
        context['parent_url'] = reverse_lazy('partners:partner_list')
        context['promos'] = obj.promo_set.all()
        return context


class ProgramPaySuccessRedirectView(HasGroupPermissionMixin, RedirectView):

    def generate(self, pk, *args, **kwargs):
        partner_obj = Partner.objects.get(id=pk)
        day_qs = CatalogOrderTime.objects.all()
        try:
            for days in day_qs:
                for i in range(0,3):
                    name = id_generator().lower()
                    promo_obj = Promo.objects.create(free=True, partner=partner_obj, name=name, catalog_order_time=days)
        except Exception as e:
            return
        return

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs['pk']
        url = reverse_lazy('partners:partner_detail', kwargs={'pk':self.kwargs['pk']})
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        self.generate(pk)
        return url



class PartnerUpdateView(HasGroupPermissionMixin, UpdateView):
    model = Partner
    form_class = PartnerForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('partners:partner_list')

    def get_context_data(self, **kwargs):
        context = super(PartnerUpdateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        context['title'] =  'Редактирование профиля партнера'
        context['parent_title'] = 'Партнеры'
        context['parent_url'] = reverse_lazy('partners:partner_list')
        return context


class PartnerDeleteView(HasGroupPermissionMixin, DeleteView):
    model = Partner

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('partners:partner_list')

    def get_context_data(self, **kwargs):
        context = super(PartnerDeleteView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        context['title'] =  'Удаление профиля партнера'
        context['parent_title'] = 'Партнеры'
        context['parent_url'] = reverse_lazy('partners:partner_list')
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.user.delete()
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


##################################################################################################################
## PROMOCODES

class PromoListView(HasGroupPermissionMixin, ListView):
    model = Promo

    def get_context_data(self, **kwargs):
        context = super(PromoListView, self).get_context_data(**kwargs)
        groups = ['brandowners','main_trainer']
        self.has_multiple_group(*groups)
        context['title'] = 'Бесплатные промокоды'
        context['addobject'] = reverse_lazy('partners:promo_create')
        context['free_objects'] = Promo.free_objects.all()
        return context

class PromoCreateView(HasGroupPermissionMixin, CreateView):
    model = Promo
    form_class = PromoForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('partners:promo_list')

    def get_context_data(self, **kwargs):
        context = super(PromoCreateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        context['title'] =  'Добавление промокода'
        context['parent_title'] = 'Промокоды'
        context['parent_url'] = reverse_lazy('partners:promo_list')
        return context

class PromoUpdateView(HasGroupPermissionMixin, UpdateView):
    model = Promo
    form_class = PromoForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('partners:promo_list')

    def get_context_data(self, **kwargs):
        context = super(PromoUpdateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        context['title'] =  'Редактирование промокода'
        context['parent_title'] = 'Промокоды'
        context['parent_url'] = reverse_lazy('partners:promo_list')
        return context


class PromoDeleteView(HasGroupPermissionMixin, DeleteView):
    model = Promo

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('partners:promo_list')

    def get_context_data(self, **kwargs):
        context = super(PromoDeleteView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        context['title'] =  'Удаление промокода'
        context['parent_title'] = 'Промокоды'
        context['parent_url'] = reverse_lazy('partners:promo_list')
        return context




