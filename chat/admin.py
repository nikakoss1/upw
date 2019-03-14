from django.contrib import admin


from .models import Thread, ChatMessage, Status


class ChatMessageAdmin(admin.ModelAdmin):
    search_fields = ('message',)


admin.site.register(Thread)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(Status)