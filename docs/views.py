# -*- coding: utf-8 -*-
from .forms import DocForm, DocImageForm
from .models import Doc, DocImage, Category
from appsettings.mixins import (
    AdministrationPermissionMixin,
    BrandOwnersContentManagersPermissionMixin,
    ComingSoonMixin,
    HasGroupPermissionMixin,
    LoginRequiredMixin,
    NotSuperuserMixin,
    TrainersContentManagersPermissionMixin,
    TrainersPermissionMixin,
    )
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from random import sample
from urllib.parse import quote_plus
from uuslug import slugify
import itertools


class DocListView(HasGroupPermissionMixin, ListView):
    model = Doc

    def get_context_data(self, **kwargs):
        context = super(DocListView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['trainers','brandowners', 'main_trainers','dietologs']
        self.has_multiple_group(*groups)

        query = self.request.GET.get("q")
        context['title'] = 'Помощь'
        context['categories'] = Category.objects.all()
        administration = ['brandowners',]
        if self.request.user.groups.filter(name__in=administration).exists():
            context['addobject'] = reverse_lazy('docs:doc_create')
        return context


class DocCreateView(HasGroupPermissionMixin, CreateView):
    model = Doc
    form_class = DocForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('docs:doc_list')

    def form_valid(self, form):
        try:
            if  form.is_valid():
                doc = form.save(commit=False)
                if doc.seo_title == '':
                    doc.seo_title = doc.title
                doc.save()
        except Exception as e:
            print(e)
        return HttpResponseRedirect(self.get_success_url(self))

    def get_context_data(self, *args, **kwargs):
        context = super(DocCreateView, self).get_context_data(*args, **kwargs)
        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        context['title'] = 'Добавление статьи документации'
        context['parent_title'] = 'Помощь'
        context['parent_url'] = reverse_lazy('docs:doc_list')
        return context


class DocDetailView(HasGroupPermissionMixin, DetailView):
    model = Doc

    def get_obj_title(self):
        obj = self.get_object()
        title = '{0}'.format(obj.title)
        return title

    def get_context_data(self, **kwargs):
        context = super(DocDetailView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['trainers','brandowners', 'main_trainers','dietologs']
        self.has_multiple_group(*groups)
        context['title'] = self.get_obj_title()
        context['parent_title'] = 'Помощь'
        context['parent_url'] = reverse_lazy('docs:doc_list')
        administration = ['brandowners', 'administration']
        if self.request.user.groups.filter(name__in=administration).exists():
            context['editobject'] = reverse_lazy('docs:doc_update', kwargs={"pk":self.get_object().id})
        return context

class DocUpdateView(HasGroupPermissionMixin, UpdateView):
    model = Doc
    form_class = DocForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('docs:doc_detail', kwargs={"pk":self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super(DocUpdateView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners', ]
        self.has_multiple_group(*groups)
        context['title'] = 'Редактировать пост'
        context['parent_title'] = 'Помощь'
        context['parent_url'] = reverse_lazy('docs:doc_list')
        return context

class DocDeleteView(HasGroupPermissionMixin, DeleteView):
    model = Doc
    success_url = '/panel/articles/'

    def get_context_data(self, **kwargs):
        context = super(DocDeleteView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        context['title'] = 'Удалить пост'
        context['parent_title'] = 'Посты'
        context['parent_url'] = reverse_lazy('docs:doc_list')
        return context

def doc_publish(request, pk):
    if not request.user.is_authenticated():
        raise Http404
    qs = Doc.objects.get(id=pk).doc_publish()
    obj = Doc.objects.get(id=pk)
    return redirect(obj)

def doc_draft(request, slug):
    if not request.user.is_authenticated():
        raise Http404
    qs = Doc.objects.get(id=pk).doc_draft()
    obj = Doc.objects.get(id=pk)
    return redirect(obj)
