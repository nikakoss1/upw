# -*- coding: utf-8 -*-
from .models import Subscriber
from django import forms
from django.core.exceptions import ValidationError


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['mail']
