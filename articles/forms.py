# -*- coding: utf-8 -*-
from .models import Article, ArticleImage
from django import forms
from django.utils.text import slugify
from django.utils.timezone import now
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content','draft',]
        widgets = {
                'content': SummernoteInplaceWidget(),
                }

        labels={
        'title':'Заголовок',
        'content':'Текст статьи',
        'seo_title':'СЕО тайтл, если не заполнить скопируется заголовок',
        }


class ArticleImageForm(forms.ModelForm):
    class Meta:
        model = ArticleImage
        fields = ['image']

        labels={
        'image':'Картинка поста',
        }

