# -*- coding: utf-8 -*-
from accounts.workout_models import *
from options.models import (
    Exercise
    )
from appsettings.models import (
    SettingsRestTime,
    )
from .templates import GENERAL_MUSCLES, M_N, M_M, M_A, F_N, F_M, F_A
from random import randrange



##################################################################################################################
## GENERAL WORKOUT GENERATOR

def make_workouts(client):
    workouts = []
    for i in range(0, 3):
        workout_obj = Workout.objects.create(client=client, general=True)
        workouts.append(workout_obj)
    return workouts

def random_obj(qs):
    qs_ids = qs.values_list('id', flat=True)
    random_index = randrange(0, len(qs_ids))
    return qs.get(id=qs_ids[random_index])

def generator(client, sex_level):
    for x in range(0,4):
        # CREATE WORKOUT
        i=1
        for workout in make_workouts(client):
            workout_template_key = 'workout{0}'.format(i)
            workout_template_value = sex_level[workout_template_key]

            # CREATE SET
            for wset_num in range(0, len(workout_template_value)):
                wset_num+=1
                wset_obj = Wset.objects.create(workout=workout, number=wset_num)
                wset_key = 'set{0}'.format(wset_num)
                wset_value = workout_template_value.get(wset_key)
                approach = wset_value.get('approach')
                for k,v in wset_value.items():
                    if 'approach' in k:
                        continue
                    cat1 = v.get('cat1', False)
                    cat2 = v.get('cat2', False)
                    cat3 = v.get('cat3', False)
                    rep = v.get('rep', False)

                    # GET QS
                    exercise_qs = Exercise.objects.filter(main_muscle__content=cat1)
                    if cat2:
                        exercise_qs = exercise_qs.filter(other_muscle__content=cat2)

                    exercise_qs = exercise_qs.filter(exercise_types=cat3)
                    rest_time = SettingsRestTime.objects.get(value=30)

                    # CREATE TRAINING OBJ
                    if exercise_qs.count() == 0:
                        continue
                    training_obj = Training.objects.create(workout=workout, wset=wset_obj, exercise=random_obj(exercise_qs), content='подходов: {0}, повторений: {1}'.format(approach, rep), rest_time=rest_time)
            i+=1
    return

def general_workout_generator(client, sex, level):
    if sex == 'M' and level == 'N':
        sex_level = M_N
    if sex == 'M' and level == 'M':
        sex_level = M_M
    if sex == 'M' and level == 'A':
        sex_level = M_A
    if sex == 'F' and level == 'N':
        sex_level = F_N
    if sex == 'F' and level == 'M':
        sex_level = F_M
    if sex == 'F' and level == 'A':
        sex_level = F_A
    generator(client, sex_level)
    return


##################################################################################################################
## DEMO WORKOUT GENERATOR

def demo_make_workouts(leaduser):
    workouts = []
    for i in range(0, 3):
        workout_obj = Workout.objects.create(leaduser=leaduser, demo=True)
        workouts.append(workout_obj)
    return workouts

def demo_random_obj(qs):
    qs_ids = qs.values_list('id', flat=True)
    random_index = randrange(0, len(qs_ids))
    return qs.get(id=qs_ids[random_index])

def demo_generator(leaduser, sex_level):
    for x in range(0,4):
        # CREATE WORKOUT
        i=1
        for workout in demo_make_workouts(leaduser):
            workout_template_key = 'workout{0}'.format(i)
            workout_template_value = sex_level[workout_template_key]

            # CREATE SET
            for wset_num in range(0, len(workout_template_value)):
                wset_num+=1
                wset_obj = Wset.objects.create(workout=workout, number=wset_num)
                wset_key = 'set{0}'.format(wset_num)
                wset_value = workout_template_value.get(wset_key)
                approach = wset_value.get('approach')
                for k,v in wset_value.items():
                    if 'approach' in k:
                        continue
                    cat1 = v.get('cat1', False)
                    cat2 = v.get('cat2', False)
                    cat3 = v.get('cat3', False)
                    rep = v.get('rep', False)

                    # GET QS
                    exercise_qs = Exercise.objects.filter(main_muscle__content=cat1)
                    if cat2:
                        exercise_qs = exercise_qs.filter(other_muscle__content=cat2)

                    exercise_qs = exercise_qs.filter(exercise_types=cat3)
                    rest_time = SettingsRestTime.objects.get(value=30)

                    # CREATE TRAINING OBJ
                    if exercise_qs.count() == 0:
                        continue
                    training_obj = Training.objects.create(workout=workout, wset=wset_obj, exercise=demo_random_obj(exercise_qs), content='подходов: {0}, повторений: {1}'.format(approach, rep), rest_time=rest_time)
            i+=1
    return








