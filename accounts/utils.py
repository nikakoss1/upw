# -*- coding: utf-8 -*-
from activities.models import Activity




def add_activity(client, new_client=None, progress=None, workout=None, foodprogram=None, workoutcomment=None, article=None, exercise_comment=None, content=''):
    try:
        activity_obj = Activity.objects.create(client=client, progress=progress, workout=workout, workoutcomment=workoutcomment, foodprogram=foodprogram, article=article, content=content)
        if new_client:
            activity_obj.client_create = True
            activity_obj.save()
            return activity_obj
    except Exception as e:
        return

