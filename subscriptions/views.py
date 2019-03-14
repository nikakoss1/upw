# -*- coding: utf-8 -*-
from .forms import (
    CustomWorkoutForm,
    CustomTrainingForm,
    FeatureForm,
    FoodProgramTemplateForm,
    FoodTemplateForm,
    ProgramCreateForm,
    ProgramUpdateForm,
    TemplateTypeForm,
    TimeTemplateForm,
    TrainingTemplateForm,
    WorkoutTemplateForm,
    WsetTemplateForm,
    WsetForm,
    )
from .models import (
    Program,
    Feature,
    WorkoutTemplate,
    WsetTemplate,
    TrainingTemplate,
    FoodProgramTemplate,
    DayTemplate,
    TimeTemplate,
    FoodTemplate,
    )
from accounts.forms import ExerciseFilterForm
from appsettings.mixins import (
    IsClientPermissionMixin,
    HasGroupPermissionMixin,
    )
from appsettings.models import (
    AppSettings,
    SettingsRestTime,
    MainMuscle,
    OtherMuscle,
    ExerciseType,
    SettingsDay,
    SettingsTime,
    Biomech,
    Vektor,
    DifficultyLevel,
    Equipment,
    WorkoutOccupation,
    )
from appsettings.utils import (
    has_groups,
    )

from accounts.models import (
    Workout,
    Wset,
    Training
    )
from options.models import (
    Exercise,
    Product,
    )
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import urlencode
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from urllib.parse import quote_plus
from uuslug import slugify
import json
import requests
from .daily_workout_generator import daily_workout_generator

def wg_template_ready(obj):
    if not obj.to_all:
        must_lst = [
            'M_N',
            'M_M',
            'M_A',
            'M_P',
            'F_N',
            'F_M',
            'F_A',
            'F_P',
        ]
        check_lst = []
        for workout_template in obj.workouttemplate_set.all():
            pair = '{0}_{1}'.format(workout_template.sex, workout_template.training_level)
            check_lst.append(pair)

        if set(must_lst) == set(check_lst):
            return True
        else:
            return False
    else:
        return obj.workouttemplate_set.all().count() > 0

def wc_template_ready(obj):
    if not obj.to_all:
        must_lst = [
            'M_N',
            'M_M',
            'M_A',
            'M_P',
            'F_N',
            'F_M',
            'F_A',
            'F_P',
        ]
        check_lst = []
        for workout in obj.workout_set.all():
            pair = '{0}_{1}'.format(workout.sex, workout.training_level)
            check_lst.append(pair)

        if set(must_lst) == set(check_lst):
            return True
        else:
            return False
    else:
        return obj.workout_set.all().count() > 0

def template_ready(obj):
    if obj.workout_set.all().count() > 0 or obj.foodprogram_set.all().count() > 0:
        return True
    else:
        return False

def program_is_checked(obj):
    if obj.program_type in ['WP','FP','FG',]:
        return True

    if obj.program_type == 'WG':
        if wg_template_ready(obj):
            daily_workout_generator(obj, 90)
            return True
        else:
            return False

    if obj.program_type == 'WC':
        return wc_template_ready(obj)

    if obj.program_type == 'MT':
        return template_ready(obj)



##################################################################################################################
## WORKOUT PROGRAMS

class ProgramListView(HasGroupPermissionMixin, ListView):
    model = Program

    def get_context_data(self, **kwargs):
        context = super(ProgramListView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        context['title'] = 'Программы'
        context['addobject'] = reverse_lazy('subscriptions:program_create')
        return context

class ProgramCreateView(HasGroupPermissionMixin, CreateView):
    model = Program
    form_class = ProgramCreateForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('subscriptions:program_update')

    def form_valid(self, form):
        if form.is_valid():
            program = form.save(commit=False)
            program.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('subscriptions:program_update', kwargs={'pk':program.id}))

    def get_context_data(self, **kwargs):
        context = super(ProgramCreateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        context['title'] =  'Добавление программы'
        context['parent_title'] = 'Программы'
        context['parent_url'] = reverse_lazy('subscriptions:program_list')
        return context


class ProgramUpdateView(HasGroupPermissionMixin, UpdateView):
    model = Program
    form_class = ProgramUpdateForm
    template_name = 'panel/includes/subscriptions/program_update_form.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('subscriptions:program_list')

    def get_context_data(self, **kwargs):
        context = super(ProgramUpdateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        context['title'] =  'Добавление программы'
        context['parent_title'] = 'Программы'
        context['parent_url'] = reverse_lazy('subscriptions:program_list')

        return context


    def form_valid(self, form):
        if form.is_valid():
            program = form.save(commit=False)
            if program.is_active:
                if program_is_checked(self.object):
                    program.save()
                    form.save_m2m()
                    return HttpResponseRedirect(reverse('subscriptions:program_list'))
            program.is_active = False
            program.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('subscriptions:program_update', kwargs={'pk':program.id}))

    def get_form_kwargs(self):
        kwargs = super(ProgramUpdateView, self).get_form_kwargs()
        kwargs.update({'pk': self.kwargs['pk']})
        return kwargs


class ProgramDetailView(HasGroupPermissionMixin, DetailView):
    model = Program

    def get_object(self, queryset=None):
        obj = super(ProgramDetailView, self).get_object(queryset=queryset)
        return obj

    def get_context_data(self, **kwargs):
        context = super(ProgramDetailView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        context['workout_templates'] = self.object.workouttemplate_set.all()
        context['workouts'] = self.object.workout_set.all()
        context['food_templates'] = self.get_object().foodprogramtemplate_set.all()

        if self.get_object().program_type in ['WG',]:
            context['add_workoutobject'] = reverse_lazy('subscriptions:workout_template_create', kwargs={'pk':self.kwargs.get('pk')})

        if self.get_object().program_type in ['WC', ]:
            context['add_workoutobject'] = reverse_lazy('subscriptions:custom_workout_create', kwargs={'pk':self.kwargs.get('pk')})

        if self.get_object().program_type in ['MT','EX']:
            context['add_workoutobject'] = reverse_lazy('subscriptions:custom_workout_create', kwargs={'pk':self.kwargs.get('pk')})
            context['add_foodobject'] = reverse_lazy('subscriptions:foodprogram_template_create', kwargs={'pk':self.kwargs.get('pk')})

        if self.get_object().program_type in ['FG',]:
            context['add_foodobject'] = reverse_lazy('subscriptions:foodprogram_template_create', kwargs={'pk':self.kwargs.get('pk')})

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['title'] = 'Шаблоны программы: {0}'.format(self.get_object().name)
        return context

class ProgramDeleteView(HasGroupPermissionMixin, DeleteView):
    model = Program

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('subscriptions:program_list')

    def get_context_data(self, **kwargs):
        context = super(ProgramDeleteView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        context['title'] =  'Удаление программы'
        context['parent_title'] = 'Программы'
        context['parent_url'] = reverse_lazy('subscriptions:program_list')
        return context


def program_workout_delete(request):
    if not has_groups(['brandowners',], request):
        return JsonResponse({})

    if request.method == 'GET' and request.is_ajax():
        program_workout_qs = Program.objects.get(id=int(request.GET.get('program_id', False))).workout_set.all()
        program_workout_qs.delete()

        data = {
                'price_id': '',
                    }
        return JsonResponse(data)
    else:
        data = {
                'message': "There is an error."
                    }
        return JsonResponse(data)


## ADD PROGRAM PRICES
def program_price_add(request, *args, **kwargs):
    if not has_groups(['brandowners',], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        price_form = PriceForm(request.POST)
        if price_form.is_valid():
                # GET DATA FROM FORM
                program_obj = Program.objects.get(id=int(request.POST.get('program_id', False)))

                # CREATE PRICE OBJ
                price_obj = price_form.save(commit=False)
                price_obj.program = program_obj
                price_obj.save()


                data = {
                        'price_id': price_obj.id,
                        'price_name': price_obj.name,
                        'price_price': price_obj.price,
                        'price_number': price_obj.number,
                            }

                return JsonResponse(data)

        else:
            data = {
                    'Form errors': price_form.errors
                        }
            return JsonResponse(data)

    return JsonResponse({})

## DELETE PROGRAM PRICES
def program_price_delete(request, *args, **kwargs):
    if not has_groups(['brandowners',], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        price_obj = Price.objects.get(id=int(request.POST.get('price_id', False)))
        price_obj.delete()
        data = {
                'price_id': price_obj.id,
                    }
        return JsonResponse(data)
    else:
        data = {
                'message': "There is an error."
                    }
        return JsonResponse(data)


## ADD PROGRAM FEATURES
def program_feature_add(request, *args, **kwargs):
    if not has_groups(['brandowners',], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        feature_form = FeatureForm(request.POST)
        if feature_form.is_valid():
                # GET DATA FROM FORM
                program_obj = Program.objects.get(id=int(request.POST.get('program_id', False)))

                # CREATE PRICE OBJ
                feature_obj = feature_form.save(commit=False)
                feature_obj.program = program_obj
                feature_obj.save()


                data = {
                        'feature_id': feature_obj.id,
                        'feature_name': feature_obj.name,
                            }

                return JsonResponse(data)

        else:
            data = {
                    'Form errors': feature_form.errors
                        }
            return JsonResponse(data)

    return JsonResponse({})


## DELETE PROGRAM FEATURES
def program_feature_delete(request, *args, **kwargs):
    if not has_groups(['brandowners',], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        feature_obj = Feature.objects.get(id=int(request.POST.get('feature_id', False)))
        feature_obj.delete()
        data = {
                'feature_id': feature_obj.id,
                    }
        return JsonResponse(data)
    else:
        data = {
                'message': "There is an error."
                    }
        return JsonResponse(data)

##################################################################################################################
## WORKOUT TEMPLATES

class WorkoutTemplateCreateView(HasGroupPermissionMixin, CreateView):
    model = WorkoutTemplate
    form_class = WorkoutTemplateForm

    def get_context_data(self, **kwargs):
        context = super(WorkoutTemplateCreateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        program_id = self.kwargs.get('pk')
        program_obj = Program.objects.get(id=program_id)
        rest_time_obj = SettingsRestTime.objects.get(value=0)
        context['form'] = WorkoutTemplateForm
        context['wset_template_form'] = WsetTemplateForm(initial={'rest_time':rest_time_obj})

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':program_id})
        context['lev2_title'] = program_obj.name
        context['title'] = 'Добавить шаблоны тренировок'
        return context

    def form_valid(self, form, *args, **kwargs):
        wset_template_form = WsetTemplateForm(self.request.POST)
        if form.is_valid() and wset_template_form.is_valid():
            program_id =self.kwargs.get('pk')
            try:
                workout_template = form.save(commit=False)
                program_obj = Program.objects.get(id=program_id)
                workout_template.program = program_obj
                new_workout_template_number = program_obj.workouttemplate_set.all().count() + 1
                workout_template.number = new_workout_template_number
                workout_template.save()
                wset_template_obj = wset_template_form.save(commit=False)
                wset_template_obj.workout_template = workout_template
                new_wset_template_number = workout_template.wsettemplate_set.all().count() + 1
                wset_template_obj.number = new_wset_template_number
                wset_template_obj.save()
            except Exception as e:
                print(e)

            if  workout_template.rest:
                return HttpResponseRedirect(reverse_lazy('subscriptions:program_detail', kwargs={'pk':program_id}))

            if  program_obj.program_type == 'WG':
                return HttpResponseRedirect(reverse_lazy('subscriptions:workout_template_update', kwargs = {'pk':program_id, 'id':workout_template.id}))


class WorkoutTemplateUpdateView(HasGroupPermissionMixin, UpdateView):
    model = WorkoutTemplate
    form_class = WorkoutTemplateForm
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        obj = super(WorkoutTemplateUpdateView, self).get_object(queryset=queryset)
        return obj

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('subscriptions:program_detail', kwargs={'pk':self.get_object().program.id})

    def get_context_data(self, **kwargs):
        context = super(WorkoutTemplateUpdateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        context['addobject'] = reverse_lazy('subscriptions:wset_template_create', kwargs={'pk':self.get_object().id})


        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':self.get_object().program.id})
        context['lev2_title'] = self.get_object().program.name
        context['title'] = self.get_object().name
        context['training_form'] = TrainingTemplateForm
        return context


class WorkoutTemplateDeleteView(HasGroupPermissionMixin, DeleteView):
    model = WorkoutTemplate
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        obj = super(WorkoutTemplateDeleteView, self).get_object(queryset=queryset)
        return obj

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('subscriptions:program_detail', kwargs={'pk':self.get_object().program.id})

    def get_context_data(self, **kwargs):
        context = super(WorkoutTemplateDeleteView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':self.get_object().program.id})
        context['lev2_title'] = self.get_object().program.name
        context['title'] = 'Удаление шаблона'
        return context


class WsetTemplateCreateView(HasGroupPermissionMixin, CreateView):
    model = WsetTemplate
    form_class = WsetTemplateForm

    def get_context_data(self, **kwargs):
        context = super(WsetTemplateCreateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        workout_template_id = self.kwargs['pk']
        workout_template_obj = WorkoutTemplate.objects.get(id=workout_template_id)
        program_obj = workout_template_obj.program

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':workout_template_obj.program.id})
        context['lev2_title'] = workout_template_obj.program.name
        context['lev3_url'] = reverse_lazy('subscriptions:workout_template_update', kwargs={'pk':workout_template_obj.program.id, 'id':workout_template_obj.id})
        context['lev3_title'] = workout_template_obj.name
        context['title'] = 'Добавить сет'
        return context

    def form_valid(self, form):
        if form.is_valid():
            wset_template_obj = form.save(commit=False)
            workout_template_id = self.kwargs['pk']
            workout_template_obj = WorkoutTemplate.objects.get(id=workout_template_id)
            new_wset_template_number = workout_template_obj.wsettemplate_set.all().count() + 1
            wset_template_obj.number = new_wset_template_number
            wset_template_obj.workout_template = workout_template_obj
            wset_template_obj.save()
        return HttpResponseRedirect(reverse_lazy('subscriptions:workout_template_update', kwargs = {'pk':workout_template_obj.program.id, 'id':workout_template_obj.id}))


## CHECK FOR EXERCISES
def get_or_none(classmodel, **kwargs):
    for k,v in kwargs.items():
        if v == '':
            return None
    try:
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None
    except Exception as e:
        return None

def make_query(content_owner_obj, workout_occupation_obj, main_muscle_obj, other_muscle_obj, exercise_type_obj, biomech_obj, vektor_obj, equipment_obj, difficulty_level_obj):
    query = Q()
    if content_owner_obj is not None:
        query &= Q(content_owner=content_owner_obj)

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

def json_template_exercise_list(request, *args, **kwargs):
    if not has_groups(['brandowners','main_trainers', 'trainers'], request):
        return JsonResponse({})

    if request.method == 'GET' and request.is_ajax():
        program_obj = Program.objects.get(id=request.GET.get('program_id'))
        content_owner_obj = program_obj.content_owner
        workout_occupation_obj = get_or_none(WorkoutOccupation, id=request.GET.get('workout_occupation'))
        main_muscle_obj = get_or_none(MainMuscle, id=request.GET.get('main_muscle'))
        other_muscle_obj = get_or_none(OtherMuscle, id=request.GET.get('other_muscle'))
        exercise_type_obj = get_or_none(ExerciseType, id=request.GET.get('exercise_type'))
        biomech_obj = get_or_none(Biomech, id=request.GET.get('biomech'))
        vektor_obj = get_or_none(Vektor, id=request.GET.get('vektor'))
        equipment_obj = get_or_none(Equipment, id=request.GET.get('equipment'))
        difficulty_level_obj = get_or_none(DifficultyLevel, id=request.GET.get('difficulty_level'))

        # MAKE COMPLEX QUERY
        query = make_query(content_owner_obj, workout_occupation_obj, main_muscle_obj, other_muscle_obj, exercise_type_obj, biomech_obj, vektor_obj, equipment_obj, difficulty_level_obj)

        # FILTER RESULTS
        try:
            exercise_qs = Exercise.objects.filter(query)
        except:
            exercise_qs = Exercise.objects.none()

        data = {}

        if exercise_qs.count() == 0:
            return JsonResponse(data)

        for exercise in exercise_qs:
            dct_name = 'dict_{0}'.format(exercise.name)
            data[dct_name] = {}
            data[dct_name]['name'] = exercise.name

            if exercise.main_muscle:
                data[dct_name]['main_muscle'] = exercise.main_muscle.content
            else:
                data[dct_name]['main_muscle'] = None

            if exercise.workout_occupation:
                data[dct_name]['workout_occupation'] = exercise.workout_occupation.name
            else:
                data[dct_name]['workout_occupation'] = None

            if exercise.other_muscle:
                data[dct_name]['other_muscle'] = exercise.other_muscle.name
            else:
                data[dct_name]['other_muscle'] = None

            if exercise.exercise_type:
                data[dct_name]['exercise_type'] = exercise.exercise_type.content
            else:
                data[dct_name]['exercise_type'] = None

            if exercise.biomech:
                data[dct_name]['biomech'] = exercise.biomech.content
            else:
                data[dct_name]['biomech'] = None

            if exercise.vektor:
                data[dct_name]['vektor'] = exercise.vektor.content
            else:
                data[dct_name]['vektor'] = None

            if exercise.equipment:
                data[dct_name]['equipment'] = exercise.equipment.content
            else:
                data[dct_name]['equipment'] = None

            if exercise.difficulty_level:
                data[dct_name]['difficulty_level'] = exercise.difficulty_level.content
            else:
                data[dct_name]['difficulty_level'] = None
        print(data)

        return JsonResponse(data)


    return JsonResponse({})

## TRAINING TEMPLATE CREATE
def training_template_create(request, *args, **kwargs):
    if not has_groups(['brandowners',], request):
        return JsonResponse({})

    if request.method == 'GET' and request.is_ajax():
        workout_template_obj = WorkoutTemplate.objects.get(id=request.GET.get('workout'))
        wset_template_obj = WsetTemplate.objects.get(id=request.GET.get('wset'))
        repetition = int(request.GET.get('repetition'))
        rest_time_obj = SettingsRestTime.objects.get(value=60)

        program_obj = Program.objects.get(id=request.GET.get('program_id'))
        content_owner_obj = program_obj.content_owner
        workout_occupation_obj = get_or_none(WorkoutOccupation, id=request.GET.get('workout_occupation'))
        main_muscle_obj = get_or_none(MainMuscle, id=request.GET.get('main_muscle'))
        other_muscle_obj = get_or_none(OtherMuscle, id=request.GET.get('other_muscle'))
        exercise_type_obj = get_or_none(ExerciseType, id=request.GET.get('exercise_type'))
        biomech_obj = get_or_none(Biomech, id=request.GET.get('biomech'))
        vektor_obj = get_or_none(Vektor, id=request.GET.get('vektor'))
        equipment_obj = get_or_none(Equipment, id=request.GET.get('equipment'))
        difficulty_level_obj = get_or_none(DifficultyLevel, id=request.GET.get('difficulty_level'))

        check_lst = [workout_occupation_obj, main_muscle_obj, other_muscle_obj, exercise_type_obj, biomech_obj, vektor_obj, equipment_obj, difficulty_level_obj]
        for obj in check_lst:
            if obj != None:
                query = make_query(
                    content_owner_obj=None,
                    workout_occupation_obj=None,
                    main_muscle_obj=None,
                    other_muscle_obj=None,
                    exercise_type_obj=None,
                    biomech_obj=None,
                    vektor_obj=None,
                    equipment_obj=None,
                    difficulty_level_obj=None
                    )
                if Exercise.objects.filter(query).count() > 0:
                    training_template_obj = TrainingTemplate.objects.create(workout_template=workout_template_obj, wset_template=wset_template_obj,workout_occupation=workout_occupation_obj, main_muscle=main_muscle_obj, other_muscle=other_muscle_obj, exercise_type=exercise_type_obj, biomech=biomech_obj, vektor=vektor_obj, equipment=equipment_obj, difficulty_level=difficulty_level_obj,  repetition=repetition, rest_time=rest_time_obj)
                    data = {
                        'training':training_template_obj.id,
                        'workout_occupation': training_template_obj.workout_occupation.name if training_template_obj.workout_occupation else '',
                        'main_muscle': training_template_obj.main_muscle.content if training_template_obj.main_muscle else '',
                        'other_muscle':training_template_obj.other_muscle.name if training_template_obj.other_muscle else '',
                        'exercise_type':training_template_obj.exercise_type.content if training_template_obj.exercise_type else '',
                        'biomech':training_template_obj.biomech.content if training_template_obj.biomech else '',
                        'vektor':training_template_obj.vektor.content if training_template_obj.vektor else '',
                        'equipment':training_template_obj.equipment.content if training_template_obj.equipment else '',
                        'difficulty_level':training_template_obj.difficulty_level.content if training_template_obj.difficulty_level else '',
                        'repetition':training_template_obj.repetition,
                    }
                    return JsonResponse(data)
        return JsonResponse({})

    return JsonResponse({})


## TRAINING TEMPLATE DELETE
def training_template_delete(request, *args, **kwargs):
    if not has_groups(['brandowners',], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        training_template_obj = TrainingTemplate.objects.get(id=int(request.POST.get('training', False)))
        training_template_obj.delete()
        data = {
                'training_template_obj': training_template_obj.id,
                    }
        return JsonResponse(data)
    else:
        data = {
                'message': "There is an error."
                    }
        return JsonResponse(data)


# ##################################################################################################################
# ## CUSTOM WORKOUT TEMPLATES

def get_program(pk):
    return Program.objects.get(id=pk)


class CustomWorkoutCreateView(HasGroupPermissionMixin, CreateView):
    model = Workout
    form_class = CustomWorkoutForm
    template_name = 'panel/includes/subscriptions/customworkout_form.html'

    def get_context_data(self, **kwargs):
        context = super(CustomWorkoutCreateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        program_id = self.kwargs.get('pk')
        program_obj = Program.objects.get(id=program_id)
        rest_time_obj = SettingsRestTime.objects.get(value=0)
        context['form'] = CustomWorkoutForm
        context['wset_form'] = WsetForm(initial={'rest_time':rest_time_obj})

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':program_id})
        context['lev2_title'] = program_obj.name
        context['title'] = 'Добавить тренировки'
        return context

    def form_valid(self, form, *args, **kwargs):
        wset_form = WsetForm(self.request.POST)
        if form.is_valid() and wset_form.is_valid():
            program_id =self.kwargs.get('pk')
            try:
                workout_obj = form.save(commit=False)
                program_obj = Program.objects.get(id=program_id)
                workout_obj.program = program_obj
                new_workout_number = program_obj.workout_set.all().count() + 1
                workout_obj.number = new_workout_number
                workout_obj.save()
                wset_obj = wset_form.save(commit=False)
                wset_obj.workout = workout_obj
                new_wset_number = workout_obj.wset_set.all().count() + 1
                wset_obj.number = new_wset_number
                wset_obj.save()
            except Exception as e:
                print(e)

            if  program_obj.program_type in ['WC', 'MT']:
                return HttpResponseRedirect(reverse_lazy('subscriptions:custom_workout_update', kwargs = {'pk':workout_obj.id}))
            else:
                return HttpResponseRedirect(reverse_lazy('subscriptions:program_detail', kwargs={'pk':program_id}))


class CustomWorkoutUpdateView(HasGroupPermissionMixin, UpdateView):
    model = Workout
    form_class = CustomWorkoutForm
    template_name = 'panel/includes/subscriptions/customworkout_detail.html'

    def get_object(self, queryset=None):
        obj = super(CustomWorkoutUpdateView, self).get_object(queryset=queryset)
        return obj

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('subscriptions:program_detail', kwargs={'pk':self.get_object().program.id})

    def get_context_data(self, **kwargs):
        context = super(CustomWorkoutUpdateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        # UPDATE KWARGS FOR WORKOUT_TEMPLATE_CREATE
        url = reverse_lazy('subscriptions:custom_wset_create', kwargs={'pk':self.kwargs['pk']})
        context['addobject'] = url

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':self.get_object().program.id})
        context['lev2_title'] = self.get_object().program.name
        context['title'] = self.get_object().name
        context['custom_training_form'] = CustomTrainingForm
        context['exercise_filter_form'] = ExerciseFilterForm
        context['wsets'] = self.get_object().wset_set.all()
        return context


class CustomWorkoutDeleteView(HasGroupPermissionMixin, DeleteView):
    model = Workout

    def get_object(self, queryset=None):
        obj = super(CustomWorkoutDeleteView, self).get_object(queryset=queryset)
        return obj

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('subscriptions:program_detail', kwargs={'pk':self.get_object().program.id})

    def get_context_data(self, **kwargs):
        context = super(CustomWorkoutDeleteView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':self.get_object().program.id})
        context['lev2_title'] = self.get_object().program.name
        context['title'] = 'Удаление шаблона'
        return context


class CustomWsetCreateView(HasGroupPermissionMixin, CreateView):
    model = Wset
    form_class = WsetForm

    def get_context_data(self, **kwargs):
        context = super(CustomWsetCreateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        custom_workout_obj = Workout.objects.get(id=self.kwargs['pk'])
        program_obj = custom_workout_obj.program

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':custom_workout_obj.program.id})
        context['lev2_title'] = custom_workout_obj.program.name
        context['lev3_url'] = reverse_lazy('subscriptions:custom_workout_update', kwargs={'pk':custom_workout_obj.program.id})
        context['lev3_title'] = custom_workout_obj.name
        context['title'] = 'Добавить сет'
        context['button'] = 'Добавить'
        return context

    def form_valid(self, form):
        if form.is_valid():
            wset_obj = form.save(commit=False)
            custom_workout_obj = Workout.objects.get(id=self.kwargs['pk'])
            new_wset_number = custom_workout_obj.wset_set.all().count() + 1
            wset_obj.number = new_wset_number
            wset_obj.workout = custom_workout_obj
            wset_obj.save()
        return HttpResponseRedirect(reverse_lazy('subscriptions:custom_workout_update', kwargs = {'pk':custom_workout_obj.id}))


class CustomWsetUpdateView(HasGroupPermissionMixin, UpdateView):
    model = Wset
    form_class = WsetForm

    def get_object(self):
        return Wset.objects.get(pk=self.kwargs['sk'])

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('subscriptions:custom_workout_update', kwargs={'pk':self.kwargs['pk']})


    def get_context_data(self,  **kwargs):
        context = super(CustomWsetUpdateView, self).get_context_data(**kwargs)
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        custom_workout_obj = Workout.objects.get(id=self.kwargs['pk'])
        program_obj = custom_workout_obj.program

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':custom_workout_obj.program.id})
        context['lev2_title'] = custom_workout_obj.program.name
        context['lev3_url'] = reverse_lazy('subscriptions:custom_workout_update', kwargs={'pk':custom_workout_obj.program.id})
        context['lev3_title'] = custom_workout_obj.name
        context['title'] = 'Редактирование сета №{0}'.format(self.object.number)
        context['button'] = 'Добавить'
        return context


def custom_training_create(request, *args, **kwargs):
    if not has_groups(['brandowners',], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        trainingform = CustomTrainingForm(request.POST)
        if trainingform.is_valid():
            # GET DATA FROM FORM
            content = request.POST.get('content', False)
            workout_obj = Workout.objects.get(id=int(request.POST.get('workout', False)))
            wset_obj = Wset.objects.get(id=int(request.POST.get('wset', False)))
            exercise_id = int(request.POST.get('exercise', False))
            exercise_obj = Exercise.objects.get(id=exercise_id)
            url = exercise_obj.short_video

            # CREATE TRAINING OBJ
            training_obj = trainingform.save(commit=False)
            training_obj.workout = workout_obj
            training_obj.content = content
            training_obj.wset = wset_obj
            training_obj.exercise = exercise_obj
            training_obj.save()


            data = {
                    'training': training_obj.id,
                    'training_delete': reverse_lazy("subscriptions:custom_training_delete"),
                    'workout': workout_obj.id,
                    'wset': wset_obj.id,
                    'excercise': training_obj.exercise.name,
                    'content': training_obj.content,
                    'rest_time': training_obj.rest_time.name,
                    'url': url,
                        }

            return JsonResponse(data)

        else:
            data = {
                    'Form errors': trainingform.errors
                        }
            return JsonResponse(data)
    else:
        trainingform = CustomTrainingForm(prefix = 'TrainingForm')
        data = {
                'message': "There is an error."
                    }
        return JsonResponse(data)


def custom_training_delete(request, *args, **kwargs):
    if not has_groups(['brandowners',], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        custom_training_obj = Training.objects.get(id=int(request.POST.get('training', False)))
        custom_training_obj.delete()
        data = {
                'training': custom_training_obj.id,
                    }
        return JsonResponse(data)
    else:
        data = {
                'message': "There is an error."
                    }
        return JsonResponse(data)


########################################################################################################################
## FOODPROGRAM CRUD

class FoodProgramTemplateCreateView(HasGroupPermissionMixin, CreateView):
    model = FoodProgramTemplate
    form_class = FoodProgramTemplateForm

    def form_valid(self, form):
        program_obj = get_program(self.kwargs['pk'])
        if form.is_valid():
            instance = form.save(commit=False)
            instance.program = program_obj
            instance.save()
        i = 0
        for day in SettingsDay.objects.all():
            DayTemplate.objects.create(name=day, foodprogram_template=instance, sorting=i)
            i+=1
        return HttpResponseRedirect(reverse_lazy('subscriptions:foodprogram_template_detail', kwargs={'pk':program_obj.id, 'id':instance.id}))

    def get_context_data(self, **kwargs):
        context = super(FoodProgramTemplateCreateView, self).get_context_data(**kwargs)

        ## CHECK IF NOT USER IN GROUP
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        program_obj = get_program(self.kwargs['pk'])
        program_id = program_obj.id

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':program_id})
        context['lev2_title'] = program_obj.name
        context['title'] = 'Добавить шаблоны питания'
        return context

class FoodProgramTemplateDetailView(HasGroupPermissionMixin, DetailView):
    model = FoodProgramTemplate
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        obj = super(FoodProgramTemplateDetailView, self).get_object(queryset=queryset)
        return obj

    def get_context_data(self,  **kwargs):
        context = super(FoodProgramTemplateDetailView, self).get_context_data(**kwargs)
        context['days'] = DayTemplate.objects.filter(foodprogram_template=self.get_object())
        context['title'] = '%s' % self.get_object().name

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners', ]
        self.has_multiple_group(*groups)
        program_obj = get_program(self.kwargs['pk'])

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':program_obj.id})
        context['lev2_title'] = program_obj.name
        context['title'] = self.get_object().name
        context['foodform'] = FoodTemplateForm
        context['timeform'] = TimeTemplateForm
        return context


class FoodProgramTemplateUpdateView(HasGroupPermissionMixin,  UpdateView):
    model = FoodProgramTemplate
    form_class = FoodProgramTemplateForm
    pk_url_kwarg = 'id'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('subscriptions:program_detail', kwargs={'pk':self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super(FoodProgramTemplateUpdateView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners', ]
        self.has_multiple_group(*groups)

        program_obj = get_program(self.kwargs['pk'])

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':program_obj.id})
        context['lev2_title'] = program_obj.name
        context['title'] = 'Редактировать программу питания {} от {}'.format(self.object.name, self.object.created)
        return context


class FoodProgramTemplateDeleteView(HasGroupPermissionMixin,  DeleteView):
    model = FoodProgramTemplate
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        obj = super(FoodProgramTemplateDeleteView, self).get_object(queryset=queryset)
        return obj

    def get_success_url(self, *args, **kwargs):
        return  reverse_lazy('subscriptions:program_detail', kwargs={'pk':self.object.program.id})

    def get_context_data(self, **kwargs):
        context = super(FoodProgramTemplateDeleteView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners', ]
        self.has_multiple_group(*groups)

        program_obj = get_program(self.kwargs['pk'])

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('subscriptions:program_list')
        context['lev1_title'] = 'Программы'
        context['lev2_url'] = reverse_lazy('subscriptions:program_detail', kwargs={'pk':program_obj.id})
        context['lev2_title'] = program_obj.name
        context['title'] = 'Удалить шаблон питания {} от {}'.format(self.object.name, self.object.created)
        return context


def food_template_create(request, *args, **kwargs):
    if not has_groups(['brandowners','trainers','dietologs','main_trainers'], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        foodform  =  FoodTemplateForm(request.POST or None)
        timeform = TimeTemplateForm(request.POST or None)
        if foodform.is_valid() and timeform.is_valid():

            # GET DATA FROM FORM
            settingstime = timeform.cleaned_data['settingstime']
            settingstime_obj = SettingsTime.objects.get(name=str(settingstime.name)[:-3])
            foodprogramеtemplate_obj = FoodProgramTemplate.objects.get(id=int(request.POST.get('foodprogram', False)))
            daytemplate_obj = DayTemplate.objects.get(id=int(request.POST.get('day', False)))
            product_obj = Product.objects.get(id=int(request.POST.get('product', False)))

            # CREATE TIME AND FOOD OBJ
            try:
                timetemplate_obj, created = TimeTemplate.objects.get_or_create(settingstime=settingstime_obj, day_template=daytemplate_obj)
                foodtemplate_obj = foodform.save(commit=False)
                foodtemplate_obj.foodprogram_template = foodprogramеtemplate_obj
                foodtemplate_obj.day_template = daytemplate_obj
                foodtemplate_obj.time_template = timetemplate_obj
                foodtemplate_obj.product = product_obj

                # UPDATE KBZU 100g
                foodtemplate_obj.kkal = foodtemplate_obj.product.kbzu_100g.kkal/100*foodtemplate_obj.weight
                foodtemplate_obj.protein = foodtemplate_obj.product.kbzu_100g.protein/100*foodtemplate_obj.weight
                foodtemplate_obj.fat = foodtemplate_obj.product.kbzu_100g.fat/100*foodtemplate_obj.weight
                foodtemplate_obj.carbohydrate = foodtemplate_obj.product.kbzu_100g.carbohydrate/100*foodtemplate_obj.weight
                product_unit = foodtemplate_obj.product.kbzu_100g.weight

                # UPDATE KBZU 1PORTION
                if product_obj.recipe:
                    foodtemplate_obj.kkal = foodtemplate_obj.product.kbzu_1portion.kkal/foodtemplate_obj.product.kbzu_1portion.weight*foodtemplate_obj.weight
                    foodtemplate_obj.protein = foodtemplate_obj.product.kbzu_1portion.protein/foodtemplate_obj.product.kbzu_1portion.weight*foodtemplate_obj.weight
                    foodtemplate_obj.fat = foodtemplate_obj.product.kbzu_1portion.fat/foodtemplate_obj.product.kbzu_1portion.weight*foodtemplate_obj.weight
                    foodtemplate_obj.carbohydrate = foodtemplate_obj.product.kbzu_1portion.carbohydrate/foodtemplate_obj.product.kbzu_1portion.weight*foodtemplate_obj.weight
                    product_unit = foodtemplate_obj.product.kbzu_1portion.weight



                foodtemplate_obj.save()
            except Exception as e:
                print(e)

            data = {
                    'food_id': foodtemplate_obj.id,
                    'food_delete': reverse_lazy("subscriptions:food_template_delete"),
                    'eattime_id': timetemplate_obj.id,
                    'product': foodtemplate_obj.product.name,
                    'product_unit': product_unit,
                    'weight': foodtemplate_obj.weight,
                    'time': settingstime_obj.name,
                    'kkal': foodtemplate_obj.kkal,
                    'protein': foodtemplate_obj.protein,
                    'fat': foodtemplate_obj.fat,
                    'carbohydrate': foodtemplate_obj.carbohydrate,
                    'time_weight': timetemplate_obj.weight,
                    'time_kkal': timetemplate_obj.kkal,
                    'time_protein': timetemplate_obj.protein,
                    'time_fat': timetemplate_obj.fat,
                    'time_carbohydrate': timetemplate_obj.carbohydrate,
                        }

            return JsonResponse(data)

        else:
            data = {
                    'message': "Form is not valid"
                        }
            return JsonResponse(data)
    else:
        foodform = FoodForm(prefix = 'FoodForm')
        timeform = TimeForm(prefix = 'TimeForm')
        data = {
                'message': "There is an error."
                    }
        return JsonResponse(data)


def food_template_delete(request, *args, **kwargs):
    if not has_groups(['brandowners','trainers','dietologs','main_trainers'], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        food_id = request.POST.get('food', False)
        eattime_id = request.POST.get('eattime', False)
        row_delete = request.POST.get('row_delete', False)
        eattime_delete = request.POST.get('eattime_delete', False)
        food_obj = FoodTemplate.objects.get(id=food_id)
        time_obj = TimeTemplate.objects.get(id=eattime_id)
        if not eattime_delete:
            # DELETE SUM KBZU FROM TIME OBJ
            time_obj.weight -= food_obj.weight
            time_obj.kkal -= food_obj.kkal
            time_obj.protein -= food_obj.protein
            time_obj.fat -= food_obj.fat
            time_obj.carbohydrate -= food_obj.carbohydrate
            food_obj.delete()
            time_obj.save()

            data = {
                    'time_weight': time_obj.weight,
                    'time_kkal': time_obj.kkal,
                    'time_protein': time_obj.protein,
                    'time_fat': time_obj.fat,
                    'time_carbohydrate': time_obj.carbohydrate,
                    'row_delete': row_delete,
                        }
        else:
            food_obj.delete()
            time_obj.delete()
            data = {
                    'eattime_delete': eattime_delete,
                        }
        return JsonResponse(data)
    else:
        data = {
                'message': "There is an error."
                    }
        return JsonResponse(data)
