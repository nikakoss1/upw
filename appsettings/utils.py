# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User, Group
from django.db.models import Q
from appsettings.models import (
    KA,
    )
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from options.models import Product
from random import randrange
from decimal import *
import string, random

def id_generator(size=8, chars='ADEFGHJKMNPQRSTWXWZ23456789'):
    return ''.join(random.choice(chars) for _ in range(size))

def get_redirect_url(request):
    redirect_to = request.POST.get('page','/')
    user = request.user
    if user.groups.filter(name__in=['brandowners','main_trainers','trainers', 'dietologs']).exists():
        return reverse_lazy('accounts:client_list')
    elif user.groups.filter(name__in=['clients',]).exists():
        return reverse_lazy('members:program_item_list')
    elif user.groups.filter(name__in=['contentmanagers',]).exists():
        return reverse_lazy('options:exercise_list')
    elif user.is_superuser:
        return '/adminkanasporte'
    elif user.groups.filter(name__in=['clients',]).exists():
        return redirect_to
    else:
        return '/lg'

def get_bok_ck(weight, age, high, training_level, sex):
    try:
        if sex == 'M':
            # bok = 66.5 + 13.75*weight + 5.003*high - 6.775*age
            bok = 10*weight + 6.25*high - 5*age + 5
        if sex == 'F':
            # bok = 655.1 + 9.563*weight + 1.85*high - 4.676*age
            bok = 10*weight + 6.25*high - 5*age - 161
        dk = bok * float(KA[training_level])
        return (bok, dk)
    except Exception as e:
        print(e)

def has_group(user, group):
    return user.groups.filter(name=group).exists()

def has_multiple_group(user, groups):
    return user.groups.filter(name__in=groups).exists()


def has_groups(groups, request):
    if request.user.is_superuser:
        return True
    try:
        for group_name in groups:
            group_obj = Group.objects.get(name=group_name)
            if group_obj in request.user.groups.all():
                return True
    except Exception as e:
        return False
    return False






