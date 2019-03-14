# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.crypto import get_random_string
from .models import Client


class Room(models.Model):
    label = models.SlugField(unique=True)
    mobileappuser = models.ForeignKey(MobileAppUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "%s" % self.label

    # def get_absolute_url(self):
    #     return reverse("chat:chat_room", kwargs={"label":self.label, "pk":self.order.id})


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages')
    client = models.ForeignKey(User, null=True, blank=True)
    handle = models.TextField()
    userhandle = models.CharField(max_length=120, blank=True, null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    new = models.BooleanField(default=True)

    def __str__(self):
        return "%s | %s" % (self.handle, self.timestamp)


    def as_dict(self):
        return {'handle': self.handle, 'message': self.message, 'timestamp': _date(self.timestamp, "d b, D"), 'userhandle':self.userhandle}

    @property
    def websocket_group(self):
        """
        Returns the Channels Group that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return Group("room-%s" % self.id)

    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)

        if preferences.MyPreferences.new_message_send_email:
            if self.userhandle == 'client':
                text = self.message
                send_notify_email(text)

        if self.userhandle == 'jurist':
            uuid = self.room.mobileappuser.uuid
            message_content = self.message
            header = {"Content-Type": "application/json; charset=utf-8",
                      "Authorization":"Basic YTllNDcwYTktMjE0ZC00NDZmLWIwODAtMmEyNmEwMjU4NGZj"}

            payload = {"app_id": "cb4a71fd-1b09-4107-bcb5-c05e659d08e6",
                       "filters": [
                            {"field": "tag", "key": "room", "relation": "=", "value": uuid},
                        ],
                       "contents": {"ru": message_content },
                       "data": { "room" : uuid }
                      }
            req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))


