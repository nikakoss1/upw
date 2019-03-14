# -*- coding: utf-8 -*-
from .models import Bloger, Status
from .forms import BlogerForm
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
from appsettings.utils import (
    get_redirect_url,
    has_groups,
    )
from appsettings.models import BLOGER_STATUS
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.base import RedirectView
from random import sample
from urllib.parse import quote_plus
from uuslug import slugify
import itertools


class BlogerListView(HasGroupPermissionMixin, ListView):
    model = Bloger
    paginate_by = 100

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        queryset = Bloger.objects.all()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                ).distinct().order_by('subs')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BlogerListView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        queryset = self.get_queryset()
        context['queryset'] = queryset
        context['title'] = 'Блогеры'
        context['statuses'] = BLOGER_STATUS
        administration = ['brandowners',]
        return context


def bloger_status(request):
    data = {}
    if not has_groups(['brandowners',], request):
        return JsonResponse({"suggestions":[{'value':'', 'data':''}]})

    if request.is_ajax():
        bloger_id = request.GET.get('bloger_id', None)
        status = request.GET.get('status', None)
        bloger_obj = Bloger.objects.get(id=bloger_id)
        bloger_obj.status = status
        bloger_obj.save()
    return JsonResponse(data)


class PromoRedirectView(RedirectView):
    def get_redirect_url(self):
        return 'https://www.instagram.com/nasporte.online/'

