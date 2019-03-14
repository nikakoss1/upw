from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        if user.is_superuser:
            return True
        elif ',' in group_name:
            groups = [group.strip() for group in group_name.split(',')]
            return user.groups.filter(name__in=groups).exists()
        else:
            return user.groups.filter(name=group_name).exists()
    except:
        pass
