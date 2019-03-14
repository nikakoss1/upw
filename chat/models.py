from accounts.models import LeadUser, Trainer, Client
from appsettings.models import WELCOME_MESSAGE
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
import json

User = get_user_model()

class ThreadManager(models.Manager):
    def get_or_new(self, leaduser, client, trainer):
        obj = self.model(leaduser=leaduser, client=client, trainer=trainer)
        thread_qs = Thread.objects.filter(leaduser=leaduser, client=client, trainer=trainer)
        if thread_qs.exists():
            return thread_qs.first(), True
        else:
            obj.save()
            return obj, True


class Thread(models.Model):
    leaduser     = models.ForeignKey(LeadUser, null=True, blank=True)
    client       = models.ForeignKey(Client, null=True, blank=True)
    trainer      = models.ForeignKey(Trainer, null=True, blank=True)
    updated      = models.DateTimeField(auto_now=True)
    timestamp    = models.DateTimeField(auto_now_add=True)

    objects      = ThreadManager()

    def __str__(self):
        return "%s" % self.id

    @property
    def room_group_name(self):
        return 'chat_{0}'.format(self.id)

    def is_first_for_leaduser(self):
        if self.leaduser.thread_set.all().count() >= 1:
            return False
        return True


def trigger_welcome_message(client, trainer):

    data = {
        "type": "welcome_message",
        "client_id": client.id,
        "trainer_id": trainer.id,
        "userhandle": 'trainer',
        "timeout": 180
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)('welcome', data)


@receiver(post_save, sender=Client)
def welcome_message_post_save(instance, created, **kwargs):
    if created:
        client = instance
        trainer = Trainer.objects.get(is_boss=True)
        trigger_welcome_message(client, trainer)
    return


class Status(models.Model):
    leaduser    = models.ForeignKey(LeadUser, null=True, blank=True)
    client      = models.ForeignKey(Client, null=True, blank=True)
    trainer     = models.ForeignKey(Trainer, null=True, blank=True)


class ChatMessage(models.Model):
    thread      = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.SET_NULL)
    leaduser    = models.ForeignKey(LeadUser, null=True, blank=True)
    client      = models.ForeignKey(Client, null=True, blank=True)
    trainer     = models.ForeignKey(Trainer, null=True, blank=True)
    message     = models.TextField(null=True, blank=True)
    userhandle  = models.CharField(max_length=120, null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    created     = models.DateField(auto_now_add=True, auto_now=False)
    updated     = models.DateField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['created']


















