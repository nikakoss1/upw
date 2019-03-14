from django import template
from options.models import Exercise

register = template.Library()

@register.filter(name='is_content_owner')
def is_content_owner(user, obj):
    try:
        trainer = user.trainer
        if trainer.is_boss:
            return True
        qs = Exercise.objects.filter(content_owner=trainer)
        if obj in qs:
            return True
        return False
    except :
        return False
