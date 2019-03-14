# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from .templates import *
from options.models import Exercise

# Create your tests here.
class TemplateTestCase(TestCase):
    # def setUp(self):
    #     Animal.objects.create(name="lion", sound="roar")
    #     Animal.objects.create(name="cat", sound="meow")

    def has_all_muscles(self):
        for workout_key,workout_value in M_N.items():
            for set_key,set_value in workout_value.items():
                for training_key, training_value in set_value.items():


