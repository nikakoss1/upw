# -*- coding: utf-8 -*-
from .models import (
    Partner,
    Promo,
    )
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, ButtonHolder, Submit, Field, HTML
from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.db.models import Q
from appsettings.utils import id_generator

class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ('trainer','content','phone','discount','promocode')
        labels = {
            'trainer':'Является ли партнер тренером',
            'content':'Описание, контакты, любая информация по партнеру',
            'phone':'Телефон',
            'discount':'Постоянная скидка на каталог от партнера',
            'promocode':'Промокод партнера',
        }


class PromoForm(forms.ModelForm):
    class Meta:
        model = Promo
        fields = (
            'partner',
            'name',
            'free',
            'catalog_order_time',
        )
        labels = {
            'partner':'Партнер',
            'name':'Название',
            'free':'Бесплатный период',
            'catalog_order_time':'Количество бесплатных дней',
        }







