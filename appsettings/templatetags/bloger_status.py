from django import template
from django.contrib.auth.models import Group
from appsettings.models import BLOGER_STATUS

register = template.Library()

def get_status_value(status):
    for item in BLOGER_STATUS:
        if item[0] == status:
            return item[1]

@register.filter(name='bloger_status')
def bloger_status(status):
    if status == 'N':
        return 'default'
    elif status == 'D':
        return 'primary'
    elif status == 'P':
        return 'success'
    elif status == 'O':
        return 'danger'
