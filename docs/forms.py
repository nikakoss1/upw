# -*- coding: utf-8 -*-
from .models import Doc, DocImage
from django import forms
from django.utils.timezone import now
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

class DocForm(forms.ModelForm):
    class Meta:
        model = Doc
        fields = [
            'category',
            'title',
            'content',
            'draft',
        ]
        widgets = {
                'content': SummernoteInplaceWidget(),
                }

        labels={
        'category':'Категория',
        'title':'Заголовок',
        'content':'Текст статьи',
        'seo_title':'СЕО тайтл, если не заполнить скопируется заголовок',
        }


class DocImageForm(forms.ModelForm):
    class Meta:
        model = DocImage
        fields = ['image']

        labels={
        'image':'Картинка статьи',
        }

