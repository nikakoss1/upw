# -*- coding: utf-8 -*-
from accounts.workout_models import *
from appsettings.models import SettingsRestTime
from datetime import date, timedelta
from django.db.models import Q
from random import randrange


today = date.today()

def workout_number(obj):
    return obj.workout_set.all().count() + 1

def get_random_id(qs_ids):
    random_index = randrange(0, len(qs_ids))
    if len(qs_ids) == 1:
        return qs_ids[0]
    return qs_ids[random_index]

def random_obj(qs, used_wset_trainings):
    lst = []
    qs_ids = list(qs.values_list('id', flat=True))
    while len(qs_ids) > 0:
        random_id = get_random_id(qs_ids)
        if random_id in used_wset_trainings:
            lst.append(random_id)
            qs_ids.remove(random_id)
            continue
        else:
            return qs.get(id=random_id)

    random_id = get_random_id(lst)
    return qs.get(id=random_id)


def make_query(workout_occupation_obj, main_muscle_obj, other_muscle_obj, exercise_type_obj, biomech_obj, vektor_obj, equipment_obj, difficulty_level_obj):
    query = Q()
    if workout_occupation_obj is not None:
        query &= Q(workout_occupation=workout_occupation_obj)

    if main_muscle_obj is not None:
        query &= Q(main_muscle=main_muscle_obj)

    if other_muscle_obj is not None:
        query &= Q(other_muscle=other_muscle_obj)

    if exercise_type_obj is not None:
        query &= Q(exercise_type=exercise_type_obj)

    if biomech_obj is not None:
        query &= Q(biomech=biomech_obj)

    if vektor_obj is not None:
        query &= Q(vektor=vektor_obj)

    if equipment_obj is not None:
        query &= Q(equipment=equipment_obj)

    if difficulty_level_obj is not None:
        query &= Q(difficulty_level=difficulty_level_obj)
    return query

def get_content(obj, exercise_type, repetition):
    program_location = obj.program_location
    program_level = obj.program_level
    if not exercise_type == None:
        if str(exercise_type) == 'Кардио':
            return '{0} минут(ы)'.format(repetition)
    if program_location == 'fitness':
        if program_level == 'start':
            return '2-3 подхода, {0} повторений'.format(repetition)

        if program_level == 'middle':
            return '3-4 подхода, {0} повторений'.format(repetition)

        if program_level == 'pro':
            return '3-4 подхода, {0} повторений'.format(repetition)

    return '1 подход, {0} повторений'.format(repetition)


def make_workouts(obj, workout_template, dates=None):
    name = workout_template.name
    sex = workout_template.sex
    training_level = workout_template.training_level
    rest = workout_template.rest
    number = workout_number(obj)

    # CREATE WORKOUTS
    if dates != None:
        gen_date = dates.pop(0)
        # if Workout.objects.filter(date=gen_date):
        #     return
        workout_obj = Workout.objects.create(program=obj, number=number, name=name, sex=sex, training_level=training_level, rest=rest, date=gen_date)
    else:
        workout_obj = Workout.objects.create(program=obj, number=number, name=name, sex=sex, training_level=training_level, rest=rest)

    # CREATE WSETS
    for wset_template in workout_template.wsettemplate_set.all():
        number = wset_template.number
        approach_number = wset_template.approach_number
        rest_time_obj = wset_template.rest_time
        wset_obj = Wset.objects.create(workout=workout_obj, number=number, approach_number=approach_number, rest_time=rest_time_obj)

        # CREATE TRAININGS
        used_wset_trainings = []
        for training_template in reversed(wset_template.trainingtemplate_set.all()):
            workout_occupation = training_template.workout_occupation
            main_muscle = training_template.main_muscle
            other_muscle = training_template.other_muscle
            exercise_type = training_template.exercise_type
            biomech = training_template.biomech
            vektor = training_template.vektor
            equipment = training_template.equipment
            difficulty_level = training_template.difficulty_level
            repetition = training_template.repetition
            rest_time_obj = SettingsRestTime.objects.get(value=training_template.rest_time.value)
            query = make_query(workout_occupation, main_muscle, other_muscle, exercise_type, biomech, vektor, equipment, difficulty_level)
            exercise_qs = Exercise.objects.filter(query)
            if exercise_qs.count() > 0:
                exercise_obj = random_obj(exercise_qs, used_wset_trainings)
                content = get_content(obj, exercise_obj.exercise_type, repetition)
                training_obj = Training.objects.create(workout=workout_obj, wset=wset_obj, exercise=exercise_obj, content=content, rest_time=rest_time_obj)
                used_wset_trainings.append(exercise_obj.id)

def daily_workout_generator(obj, day_number):
    dates = []
    workout_template_qs = obj.workouttemplate_set.all()
    for day in range(day_number):
        now_date = today + timedelta(day)
        dates.append(now_date)

    if obj.daily:
        while len(dates) > 0:
            for workout_template in workout_template_qs:
                if len(dates) > 0:
                    make_workouts(obj, workout_template, dates)
                else:
                    break
    else:
        for workout_template in workout_template_qs:
            make_workouts(obj, workout_template)
    return












