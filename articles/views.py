# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
# from django.utils.encoding import python_2_unicode_compatible
from .forms import ArticleForm, ArticleImageForm
from .models import Article, ArticleImage
from accounts.models import Client
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
from accounts.models import Trainer
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

def get_user_ids(trainer):
    user_ids = []
    clients = Client.objects.filter(trainer=trainer)
    for client in clients:
        user_ids.append(client.user.id)
    return user_ids

### ARTICLES AT PANEL ###
class ArticleListView(HasGroupPermissionMixin, ListView):
    model = Article

    def get_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset' or 'model'"
                                       % self.__class__.__name__)
        try:
            trainer = self.request.user.trainer
            trainer_users = get_user_ids(trainer)
            qs_trainer = Article.objects.filter(draft=False, user__trainer=trainer)
            qs_users = Article.objects.filter(draft=False, user__id__in=trainer_users)
            queryset = qs_trainer|qs_users
        except Exception as e:
            trainer = Trainer.objects.get(is_boss=True)
            trainer_users = get_user_ids(trainer)
            qs_trainer = Article.objects.filter(draft=False, user__trainer=trainer)
            qs_users = Article.objects.filter(draft=False, user__id__in=trainer_users)
            queryset = qs_trainer|qs_users

        return queryset

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','main_trainers','trainers','contentmanagers']
        self.has_multiple_group(*groups)

        query = self.request.GET.get("q")
        queryset = self.get_queryset()
        if query:
            context['queryset'] = queryset.filter(
                Q(title__icontains=query)
                ).distinct().order_by('title')
        else:
            context['queryset'] = queryset
        context['title'] = 'Посты'
        context['addobject'] = reverse_lazy('articles:article_create')
        return context


class ArticleCreateView(HasGroupPermissionMixin, CreateView):
    model = Article
    form_class = ArticleForm
    second_form_class = ArticleImageForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('articles:article_list')

    def form_valid(self, form):
        try:
            imageform = ArticleImageForm(self.request.POST, self.request.FILES)
            if imageform.is_valid() and form.is_valid():
                image = imageform.save(commit=False)
                article = form.save(commit=False)
                if article.seo_title == '':
                    article.seo_title = article.title
                article.user = self.request.user
                article.save()
                image.article = article
                image.save()
        except Exception as e:
            print(e)
        return HttpResponseRedirect(self.get_success_url(self))

    def get_context_data(self, *args, **kwargs):
        context = super(ArticleCreateView, self).get_context_data(*args, **kwargs)
        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','main_trainers','trainers','contentmanagers']
        self.has_multiple_group(*groups)

        context['title'] = 'Добавление поста'
        context['imageform'] = ArticleImageForm
        context['parent_title'] = 'Посты'
        context['parent_url'] = reverse_lazy('articles:article_list')
        return context


class ArticleDetailView(HasGroupPermissionMixin, DetailView):
    model = Article

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','trainers','contentmanagers']
        self.has_multiple_group(*groups)
        context['title'] = 'Пост'
        context['parent_title'] = 'Посты'
        context['parent_url'] = reverse_lazy('articles:article_list')
        return context

class ArticleUpdateView(HasGroupPermissionMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    second_form_class = ArticleImageForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('articles:article_detail', kwargs={"slug":self.object.slug})

    def form_valid(self, form):
        imageform = ArticleImageForm(self.request.FILES)
        if form.is_valid() and imageform.is_valid():
            instance = form.save(commit=False)
            if instance.seo_title == '':
                instance.seo_title = instance.title
            imageform.article = instance
            instance.save()
            imageform.save()
        return HttpResponseRedirect(self.get_success_url(self))

    def get_context_data(self, **kwargs):
        context = super(ArticleUpdateView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','main_trainers','trainers','contentmanagers']
        self.has_multiple_group(*groups)
        context['title'] = 'Редактировать пост'
        context['parent_title'] = 'Посты'
        context['parent_url'] = reverse_lazy('articles:article_list')
        return context

class ArticleDeleteView(HasGroupPermissionMixin, DeleteView):
    model = Article
    success_url = '/panel/articles/'

    def get_context_data(self, **kwargs):
        context = super(ArticleDeleteView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','main_trainers','trainers','contentmanagers']
        self.has_multiple_group(*groups)

        context['title'] = 'Удалить пост'
        context['parent_title'] = 'Посты'
        context['parent_url'] = reverse_lazy('articles:article_list')
        return context

def article_publish(request, slug):
    if not request.user.is_authenticated():
        raise Http404
    qs = Article.objects.get(slug=slug).article_publish()
    obj = Article.objects.get(slug=slug)
    return redirect(obj)

def article_draft(request, slug):
    if not request.user.is_authenticated():
        raise Http404
    qs = Article.objects.get(slug=slug).article_draft()
    obj = Article.objects.get(slug=slug)
    return redirect(obj)

class PostListView(ComingSoonMixin, ListView):
    model = Article
    template_name = 'blog/blog_list.html'
    paginate_by = 10

    def get_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset' or 'model'"
                                       % self.__class__.__name__)

        trainer = Trainer.objects.get(is_boss=True)
        trainer_users = get_user_ids(trainer)
        qs_trainer = Article.objects.filter(draft=False, user__trainer=trainer)
        qs_users = Article.objects.filter(draft=False, user__id__in=trainer_users)
        queryset = qs_trainer|qs_users

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['title'] = 'Лента'
        context['seo_title'] = 'Лента участников'
        return context

class PostDetailView(ComingSoonMixin, DetailView):
    model = Article
    template_name = 'blog/blog_single.html'

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'slug': self.object.slug})

    def get_object(self, queryset=None):
        object = super(PostDetailView, self).get_object(queryset=queryset)
        if object.draft == True:
            raise Http404()
        return object

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['seo_title'] = '%s' % self.object.title
        return context