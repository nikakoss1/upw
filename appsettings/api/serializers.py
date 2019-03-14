# -*- coding: utf-8 -*-
from rest_framework import serializers
from appsettings.models import CompetitionStatus, AppSettings


class AppsettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSettings
        fields = [
            'brand',
            'logo1',
            'logo2',
            'coming_soon',
            'maintenance',
            'oferta',
            'general_workout_exercise_rest_time',
            'new_message_send_email',
            'rekv',
        ]