from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='qs_item')
def qs_item(qs, item):
    try:
        return qs[item]
    except:
        return None