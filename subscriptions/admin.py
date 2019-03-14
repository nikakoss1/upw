# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import (
    WorkoutTemplate,
    WsetTemplate,
    TrainingTemplate,
    Program,
    FoodProgramTemplate,
    FoodTemplate,
    TimeTemplate,
    Category,
    Favourite,
    )

admin.site.register(Program)
admin.site.register(WorkoutTemplate)
admin.site.register(WsetTemplate)
admin.site.register(TimeTemplate)
admin.site.register(TrainingTemplate)
admin.site.register(FoodProgramTemplate)
admin.site.register(FoodTemplate)
admin.site.register(Category)
admin.site.register(Favourite)


