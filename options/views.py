# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from urllib.parse import quote
from .forms import MuscleForm, ExerciseForm, FitnessClubForm, FitnessClubImageForm, ProductForm, CompetitionForm
from .models import Muscle, Exercise, FitnessClub, FitnessClubImage, Product, Competition
from appsettings.mixins import (
    BrandOwnersPermissionMixin,
    BrandOwnersContentManagersPermissionMixin,
    HasGroupPermissionMixin,
    ContentOwnerPermissionMixin,
    IsContentOwnerMixin,
    )
from accounts.models import Trainer
from django.conf import settings
from uuslug import slugify
from django.core.urlresolvers import reverse_lazy

class MuscleDetailView(BrandOwnersContentManagersPermissionMixin, DetailView):
    model = Muscle

    def get_context_data(self, *args, **kwargs):
        context = super(MuscleDetailView, self).get_context_data(*args, **kwargs)
        obj = self.get_object()
        queryset = Exercise.objects.all()
        muscle_queryset = obj.exercise_set.all()
        query = self.request.GET.get("q")
        context['object_list'] = muscle_queryset
        if query:
            context['object_list'] = queryset.filter(
                Q(name__icontains=query)
                ).distinct().order_by('name')

        context['title'] = 'Упражнения на группу мышц: %s' % obj.name
        context['muscles'] = Muscle.objects.all()
        return context

class MuscleCreateView(BrandOwnersContentManagersPermissionMixin, CreateView):
    model = Muscle
    form_class = MuscleForm
    success_message = 'Добавлена группа мышц'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('options:muscle_create')


    def get_context_data(self, *args, **kwargs):
        context = super(MuscleCreateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Группы мышц'
        context['muscles'] = Muscle.objects.all()
        return context

class MuscleUpdateView(BrandOwnersContentManagersPermissionMixin, UpdateView):
    model = Muscle
    form_class = MuscleForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('options:muscle_create')

    def get_context_data(self, *args, **kwargs):
        context = super(MuscleUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Редактирование группы мышц'
        return context

class MuscleDeleteView(BrandOwnersContentManagersPermissionMixin, DeleteView):
    model = Muscle

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('options:muscle_create')

    def get_context_data(self, *args, **kwargs):
        context = super(MuscleDeleteView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Удаление группы мышц'
        return context


class ExerciseListView(HasGroupPermissionMixin, ListView):
    model = Exercise

    def qs_by_content_owner(self):
        try:
            all_qs = Exercise.objects.all()
            boss_trainer = Trainer.objects.get(is_boss=True)
            trainer = self.request.user.trainer

            ## GET OWN CONTENT
            qs = all_qs.filter(content_owner=trainer)

            ## ADD SPORTAPPS CONTENT
            qs = qs|all_qs.filter(content_owner=boss_trainer)
            qs = qs.distinct()

        except Exception as e:
            qs = Exercise.objects.none()
        return qs

    def get_context_data(self,  **kwargs):
        context = super(ExerciseListView, self).get_context_data(**kwargs)
        groups = ['trainers','brandowners','main_trainers','contentmanagers']
        self.has_multiple_group(*groups)
        context['object_list'] = self.qs_by_content_owner()
        context['title'] = 'Упражнения'
        context['addobject'] = reverse_lazy('options:exercise_create')
        return context


class ExerciseCreateView(HasGroupPermissionMixin, CreateView):
    model = Exercise
    form_class = ExerciseForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('options:exercise_list')

    def form_valid(self, form):
        excercise_obj = form.save(commit=False)
        excercise_obj.content_owner = self.request.user.trainer
        excercise_obj.approved = True
        excercise_obj.save()
        return super(ExerciseCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ExerciseCreateView, self).get_context_data(**kwargs)
        groups = ['trainers','brandowners','main_trainers','contentmanagers']
        self.has_multiple_group(*groups)
        context['title'] = 'Добавить упражнение'
        context['parent_title'] = 'Упражнения'
        context['parent_url'] = reverse_lazy('options:exercise_list')
        return context

    def get_form_kwargs(self):
        kwargs = super(ExerciseCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class ExerciseDetailView(HasGroupPermissionMixin, DetailView):
    model = Exercise

    def get_object(self, queryset=None):
        obj = super(ExerciseDetailView, self).get_object(queryset=queryset)
        return obj

    def get_context_data(self,  **kwargs):
        context = super(ExerciseDetailView, self).get_context_data(**kwargs)
        groups = ['trainers','brandowners','main_trainers','contentmanagers']
        self.has_multiple_group(*groups)
        obj = self.get_object()
        context['title'] = '%s' % obj.name
        context['parent_title'] = 'Упражнения'
        context['parent_url'] = reverse_lazy('options:exercise_list')
        return context


class ExerciseUpdateView(HasGroupPermissionMixin, IsContentOwnerMixin, UpdateView):
    model = Exercise
    form_class = ExerciseForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('options:exercise_list')

    def get_context_data(self, **kwargs):
        context = super(ExerciseUpdateView, self).get_context_data(**kwargs)
        groups = ['trainers','brandowners','main_trainers','contentmanagers']
        self.has_multiple_group(*groups)
        context['page_title'] = 'Редактировать упражнение'
        context['title'] = self.object
        context['parent_title'] = 'Упражнения'
        context['parent_url'] = reverse_lazy('options:exercise_list')
        return context

    def form_valid(self, form):
        excercise_obj = form.save(commit=False)
        boss_trainer = Trainer.objects.get(is_boss=True)
        if self.request.user.trainer != boss_trainer:
            excercise_obj.approved = False
        excercise_obj.save()
        return super(ExerciseUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ExerciseUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class ExerciseDeleteView(HasGroupPermissionMixin, IsContentOwnerMixin, DeleteView):
    model = Exercise

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('options:exercise_list')

    def get_context_data(self, **kwargs):
        context = super(ExerciseDeleteView, self).get_context_data(**kwargs)
        groups = ['trainers','brandowners','main_trainers','contentmanagers']
        self.has_multiple_group(*groups)
        obj = self.get_object()
        self.is_content_owner(obj)
        context['title'] = 'Удаление упражнения: %s ' % self.object
        context['parent_title'] = 'Упражнения'
        context['parent_url'] = reverse_lazy('options:exercise_list')
        return context


### Products
class ProductListView(HasGroupPermissionMixin, ListView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        groups = ['brandowners','main_trainers','contentmanagers','dietologs']
        self.has_multiple_group(*groups)
        query = self.request.GET.get("q")
        queryset = Product.objects.all()
        if query:
            context['object_list'] = queryset.filter(
                Q(name__icontains=query)
                ).distinct().order_by('name')
        else:
            context['object_list'] = queryset.order_by('name')
        context['title'] = 'Справочник продуктов'
        context['addobject'] = reverse_lazy('options:product_create')
        return context

class ProductCreateView(HasGroupPermissionMixin, CreateView):
    model = Product
    form_class = ProductForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('options:product_list')

    def get_context_data(self, **kwargs):
        context = super(ProductCreateView, self).get_context_data(**kwargs)
        groups = ['brandowners','main_trainers','contentmanagers','dietologs']
        self.has_multiple_group(*groups)
        context['title'] = 'Добавить продукт'
        context['parent_title'] = 'Продукты'
        context['parent_url'] = reverse_lazy('options:product_list')
        return context


class ProductUpdateView(HasGroupPermissionMixin, UpdateView):
    model = Product
    form_class = ProductForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('options:product_list')

    def get_context_data(self, **kwargs):
        context = super(ProductUpdateView, self).get_context_data(**kwargs)
        groups = ['brandowners','main_trainers','contentmanagers','dietologs']
        self.has_multiple_group(*groups)
        context['title'] = 'Редактировать продукт: %s' % self.object
        context['parent_title'] = 'Продукты'
        context['parent_url'] = reverse_lazy('options:product_list')
        return context


class ProductDeleteView(HasGroupPermissionMixin, DeleteView):
    model = Product

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('options:product_list')

    def get_context_data(self, **kwargs):
        context = super(ProductDeleteView, self).get_context_data(**kwargs)
        groups = ['brandowners','main_trainers','contentmanagers','dietologs']
        self.has_multiple_group(*groups)
        context['title'] = 'Удалить продукт'
        context['parent_title'] = 'Продукты'
        context['parent_url'] = reverse_lazy('options:product_list')
        return context

