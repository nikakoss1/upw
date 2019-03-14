# -*- coding: utf-8 -*-
from django import forms
from django.utils.timezone import now
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from crispy_forms.helper import FormHelper

# class BlogerForm(forms.ModelForm):
#     class Meta:
#         model = Bloger
#         fields = ['name', 'status',]


#     def __init__(self, *args, **kwargs):
#         super(BlogerForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_show_labels = False
#         self.fields.get('status').widget.attrs['class'] = 'bloger-status'
