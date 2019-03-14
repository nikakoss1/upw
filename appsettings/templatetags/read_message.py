from django import template
from chat.models import ChatMessage
from django.contrib.auth import get_user_model
register = template.Library()
User  = get_user_model()


def get_reader(user):
    if user.client:
        return user.client
    elif user.trainer:
        return user.trainer
    else:
        return False

@register.filter(name='read_message')
def read_message(message_id, user_id):
    try:
        user = User.objects.get(id=user_id)
        reader = get_reader(user)
        if not reader:
            return False
        else:
            chatmessage = ChatMessage.objects.get(id=message_id)
            chatmessage.status
    except:
        pass
