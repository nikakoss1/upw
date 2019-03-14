from .models import Thread, ChatMessage
from accounts.models import LeadUser, Client, Trainer
from appsettings.models import WelcomeMessage
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseForbidden
import asyncio
import json
from .onesygnal import send_push_message
from django.core import mail
from celery.task.control import revoke
from sportapps.celery import app


## GLOBAL
User = get_user_model()

class LeadUserConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        pk  = self.scope['url_route']['kwargs']['pk']
        self.leaduser = await self.get_leaduser(pk)
        self.client = None
        self.trainer = await self.get_trainer()
        user = self.scope['user']
        if user == self.trainer.user:
            thread_obj = await self.get_thread(self.leaduser, self.client, self.trainer)
            self.cfe_chat_thread = thread_obj
            self.room_group_name = thread_obj.room_group_name # group

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.send({
                "type": "websocket.accept"
            })


    async def websocket_receive(self, event): # websocket.receive
        message_data = json.loads(event['text'])
        userhandle = message_data['userhandle']
        self.message = message_data['message']
        trainer_read = message_data.get('trainer_read', False)
        task_id = message_data.get('task_id', False)

        if trainer_read:

            # REMOVE TASK MAIL FROM QUEUE
            await self.revoke_task(task_id)

            # REMOVE TRAINER READ FLAG
            message_data.pop('trainer_read')
            await self.trainer_read(self.leaduser)
            return

        # FROM TRAINER
        if 'trainer' in userhandle:
            obj = await self.create_chat_message(
                self.cfe_chat_thread,
                self.leaduser,
                self.client,
                self.trainer,
                self.message,
                userhandle
                )

            self.leaduser.new_messages_from_trainer = True
            self.leaduser.save()

            message_data["timestamp"] = obj.timestamp.strftime('%d/%m/%Y - %H:%M')
            final_message_data = json.dumps(message_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': final_message_data
                }
            )

            # SEND PUSH
            tag = 'lead_id'
            tag_value = self.leaduser.id
            res = await send_push_message(self.message, tag, tag_value)

        # FROM LEADUSER
        else:

            # SEND MESSAGE TO TRAINER
            task_id = await self.send_mail(self.leaduser, self.message)

            # CREATE  MESSAGE IN DB
            obj = await self.create_chat_message(
                self.cfe_chat_thread,
                self.leaduser,
                self.client,
                self.trainer,
                self.message,
                userhandle
                )

            self.leaduser.new_messages_from_client = True
            self.leaduser.save()

            message_data["task_id"] = task_id
            message_data["timestamp"] = obj.timestamp.strftime('%d/%m/%Y - %H:%M')
            final_message_data = json.dumps(message_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': final_message_data
                }
            )

    async def chat_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['message']
        })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        raise StopConsumer()

    @database_sync_to_async
    def revoke_task(self, task_id):
        return revoke(task_id, terminate=True)
        # return app.control.revoke(task_id)

    @database_sync_to_async
    def send_mail(self, leaduser, message):
        boss_trainer = Trainer.objects.get(is_boss=True)
        title = 'Новое сообщение от лида №{0}'.format(leaduser.id)
        from_mail = 'nasporte.online@gmail.com'
        to_mail = boss_trainer.user.email
        emails = (
            (
                title,
                message,
                from_mail,
                [to_mail]
                ),
            )
        results = mail.send_mass_mail(emails)
        return results[0].id

    @database_sync_to_async
    def trainer_read(self, leaduser):
        leaduser.new_messages_from_client = False
        leaduser.save()

    @database_sync_to_async
    def change_status(self, client):
        client.new_messages = True
        client.save()
        return True

    @database_sync_to_async
    def get_trainer(self):
        return Trainer.objects.get(is_boss=True)

    @database_sync_to_async
    def get_leaduser(self, pk):
        return LeadUser.objects.get(id=pk)

    @database_sync_to_async
    def get_thread(self, leaduser, client, trainer):
        return Thread.objects.get_or_new(leaduser, client, trainer)[0]

    @database_sync_to_async
    def create_chat_message(self, thread, leaduser, client, trainer, message, userhandle):
        return ChatMessage.objects.create(thread=thread, leaduser=leaduser, client=client, trainer=trainer, message=message, userhandle=userhandle )


#######################################
## CLIENT CONSUMERS

class ClientConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        slug = self.scope['url_route']['kwargs']['slug']
        self.leaduser = None
        self.client = await self.get_client(slug)
        self.trainer = self.client.trainer
        user = self.scope['user']
        if user == self.trainer.user:
            thread_obj = await self.get_thread(self.leaduser, self.client, self.trainer)
            self.cfe_chat_thread = thread_obj
            self.room_group_name = thread_obj.room_group_name # group

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.send({
                "type": "websocket.accept"
            })


    async def websocket_receive(self, event): # websocket.receive
        message_data = json.loads(event['text'])
        userhandle = message_data['userhandle']
        self.message = message_data['message']
        trainer_read = message_data.get('trainer_read', False)
        from_server = message_data.get('from_server', False)
        task_id = message_data.get('task_id', False)

        if trainer_read:

            # REMOVE TASK MAIL FROM QUEUE
            await self.revoke_task(task_id)

            # REMOVE TRAINER READ FLAG
            message_data.pop('trainer_read')
            await self.trainer_read(self.client)
            return

        # FROM TRAINER
        if 'trainer' in userhandle:
            obj = await self.create_chat_message(
                self.cfe_chat_thread,
                self.leaduser,
                self.client,
                self.trainer,
                self.message,
                userhandle
                )

            self.client.new_messages_from_trainer = True
            self.client.save()

            message_data["timestamp"] = obj.timestamp.strftime('%d/%m/%Y - %H:%M')
            final_message_data = json.dumps(message_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': final_message_data
                }
            )

            # SEND PUSH
            tag = 'user_slug'
            tag_value = self.client.slug
            res = await send_push_message(self.message, tag, tag_value)

        # FROM CLIENT
        else:

            # SEND MESSAGE TO TRAINER
            task_id = await self.send_mail(self.client, self.message)

            # CREATE  MESSAGE IN DB
            obj = await self.create_chat_message(
                self.cfe_chat_thread,
                self.leaduser,
                self.client,
                self.trainer,
                self.message,
                userhandle
                )

            self.client.new_messages_from_client = True
            self.client.save()

            message_data["task_id"] = task_id
            message_data["timestamp"] = obj.timestamp.strftime('%d/%m/%Y - %H:%M')
            final_message_data = json.dumps(message_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': final_message_data
                }
            )

    async def chat_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['message']
        })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        raise StopConsumer()

    @database_sync_to_async
    def revoke_task(self, task_id):
        return revoke(task_id, terminate=True)
        # return app.control.revoke(task_id)

    @database_sync_to_async
    def send_mail(self, client, message):
        title = 'Новое сообщение от {0}'.format(client.user.get_full_name())
        from_mail = 'nasporte.online@gmail.com'
        to_mail = client.trainer.user.email
        emails = (
            (
                title,
                message,
                from_mail,
                [to_mail]
                ),
            )
        results = mail.send_mass_mail(emails)
        return results[0].id

    @database_sync_to_async
    def trainer_read(self, client):
        client.new_messages_from_client = False
        client.save()

    @database_sync_to_async
    def change_status(self, client):
        client.new_messages = True
        client.save()
        return True

    @database_sync_to_async
    def get_client(self, slug):
        return Client.objects.get(slug=slug)

    @database_sync_to_async
    def get_thread(self, leaduser, client, trainer):
        return Thread.objects.get_or_new(leaduser, client, trainer)[0]

    @database_sync_to_async
    def create_chat_message(self, thread, leaduser, client, trainer, message, userhandle):
        return ChatMessage.objects.create(thread=thread, leaduser=leaduser, client=client, trainer=trainer, message=message, userhandle=userhandle )


class WelcomeConsumer(AsyncConsumer):
    async def welcome_message(self, event):
        message_data = {}
        message = event.get("message")
        userhandle = event.get("userhandle")
        client_id = event.get('client_id')
        trainer_id = event.get('trainer_id')
        client = await self.get_client(client_id)
        trainer = await self.get_trainer(trainer_id)
        leaduser = None
        thread = await self.get_thread(leaduser, client, trainer)
        self.room_group_name = thread.room_group_name

        messages = WelcomeMessage.objects.all()
        for item in messages:
            await asyncio.sleep(120)
            message = item.content.strip()
            obj = await self.create_chat_message(thread, leaduser, client, trainer, message, userhandle)
            message_data["timestamp"] = obj.timestamp.strftime('%d/%m/%Y - %H:%M')
            message_data['message'] = message
            message_data['userhandle'] = userhandle
            message_data['handle'] = trainer.user.get_full_name()
            final_message_data = json.dumps(message_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': final_message_data
                }
            )
            client.new_messages_from_trainer = True
            client.save()

            # SEND PUSH
            tag = 'user_slug'
            tag_value = client.slug
            res = await send_push_message(message, tag, tag_value)

    async def chat_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['message']
        })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    @database_sync_to_async
    def get_client(self, client_id):
        return Client.objects.get(id=client_id)

    @database_sync_to_async
    def get_trainer(self, trainer_id):
        return Trainer.objects.get(id=trainer_id)

    @database_sync_to_async
    def get_thread(self, leaduser, client, trainer):
        return Thread.objects.get_or_new(leaduser, client, trainer)[0]

    @database_sync_to_async
    def create_chat_message(self, thread, leaduser, client, trainer, message, userhandle):
        return ChatMessage.objects.create(thread=thread, leaduser=leaduser, client=client, trainer=trainer, message=message, userhandle=userhandle )






