# -*- coding: utf-8 -*-
import logging
from .forms import (
    ClientChangeTrainerForm,
    ClientForm,
    FoodForm,
    FoodProgramCloneForm,
    FoodProgramForm,
    LeadUserForm,
    NoteForm,
    ProgressForm,
    PersonalWorkoutProfileForm,
    PersonalNutrimentProfileForm,
    TimeForm,
    TrainerForm,
    HelpTrainerForm,
    TrainingForm,
    UserChangeForm,
    UserCreationForm,
    WorkoutCloneForm,
    WorkoutForm,
    WsetForm,
    PersonalWorkoutCounter,
    PersonalNutrimentCounter,
    ExerciseFilterForm,
    )
from .mixins import AjaxFoodFormMixin
from .models import (
    Client,
    Day,
    ExerciseComment,
    Food,
    FoodProgram,
    # GeneralNutrimentProfile,
    # GeneralWorkoutProfile,
    LeadUser,
    Note,
    PersonalNutrimentProfile,
    PersonalWorkoutProfile,
    Progress,
    Time,
    Trainer,
    Training,
    Workout,
    Wset,
    )
from subscriptions.forms import TrainingTemplateForm
from activities.models import Activity
from appsettings.mixins import (
    AdministrationPermissionMixin,
    BrandOwnersPermissionMixin,
    ClientListOfTrainerPermissionMixin,
    ClientOwnerPermissionMixin,
    HasGroupPermissionMixin,
    LeadUserPermissionMixin,
    TrainersPermissionMixin,
    PersonalWorkoutProgramExist,
    PersonalFoodProgramExist,
    WorkoutCounterPositive,
    NutrimentCounterPositive,
    has_group,
    IsYourTrainerPermissionMixin,
    IsYourClientPermissionMixin,
    )
from appsettings.models import (
    SettingsDay,
    SettingsTime,
    ExerciseCommentName,
    SettingsRestTime,
    LEVELS,
    KA,
    )
from appsettings.utils import (
    get_redirect_url,
    has_groups,
    has_multiple_group,
    )
from chat.models import Thread, ChatMessage
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import login as auth_login
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from options.models import Product, Exercise
from preferences import preferences
from subscriptions.models import (
    Program,
    )
from urllib.parse import quote
from uuslug import slugify
import itertools
import json
import requests, calendar, random
from  datetime import date
from django.views.decorators.csrf import csrf_exempt


today = date.today()

logger = logging.getLogger(__name__)


def custom_login(request, template_name='registration/login.html',
          authentication_form=AuthenticationForm):

    if request.user.is_authenticated():
        return redirect(get_redirect_url(request))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')

            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            ''' End reCAPTCHA validation '''

            if result['success']:
                pass
                # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())
        return redirect(get_redirect_url(request))
    else:
        form = authentication_form(request)

    context = {
        'form': form,
    }
    return render(request, template_name, context)

def get_month(param):
    if param == 'this':
        month = today.month
    elif param == 'last':
        month = today.month - 1
        if month == 0:
            month = 12
    return month

### CLIENTS ###
class ClientListView(HasGroupPermissionMixin, ListView):
    model = Client
    paginate_by = 100

    def get_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset' or 'model'" % self.__class__.__name__)


        ### CUSTOMIZATION
        user = self.request.user
        if not has_group(user, 'brandowners'):
            if has_group(user, 'main_trainers'):
                trainer = user.trainer
                help_trainers = trainer.trainer_set.all()
                queryset = queryset.filter(
                    Q(trainer=trainer)|
                    Q(trainer__in=help_trainers)
                    )

            elif has_multiple_group(user, ['trainers','dietologs']):
                trainer = user.trainer
                queryset = queryset.filter(trainer=trainer)


        ### FILTER BY ACTIVE
        param = self.request.GET.get('active', None)
        if param != None:
            month = get_month(param)
            queryset = queryset.filter(
                Q(workout__created__month=month, workout__program__program_type='WP')|
                Q(workout__updated__month=month, workout__program__program_type='WP')|
                Q(foodprogram__created__month=month, foodprogram__program__program_type='FP')|
                Q(foodprogram__updated__month=month, foodprogram__program__program_type='FP')
                ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(ClientListView, self).get_context_data(**kwargs)
        groups = ['brandowners','main_trainers','trainers','dietologs']
        self.has_multiple_group(*groups)
        context['title'] = 'Клиенты'
        return context


class ClientDetailView(HasGroupPermissionMixin, IsYourClientPermissionMixin, DetailView):
    model = Client
    form_class = FoodForm

    def get_object(self, queryset=None):

        if queryset is None:
            queryset = self.get_queryset()
        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)
        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})
        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        return obj

    def get_messages(self, *args, **kwargs):
        client = self.get_object()
        client.new_messages_from_client = False
        client.save()
        leaduser = client.leaduser
        boss_trainer = Trainer.objects.get(is_boss=True)
        trainer = client.trainer

        if leaduser != None:
            leaduser_thread_qs = Thread.objects.filter(leaduser=leaduser, trainer=boss_trainer)
        else:
            leaduser_thread_qs = Thread.objects.none()

        leaduser_thread_obj = None
        if leaduser_thread_qs.exists():
            leaduser_thread_obj = leaduser_thread_qs[0]

        client_thread_qs = Thread.objects.filter(client=client, trainer=trainer)
        client_thread_obj = None
        if client_thread_qs.exists():
            client_thread_obj = client_thread_qs[0]

        messages = ChatMessage.objects.filter(
            Q(thread=leaduser_thread_obj)|
            Q(thread=client_thread_obj)
            ).distinct()
        return messages.order_by('-timestamp')[:300]

    def get_context_data(self, **kwargs):
        context = super(ClientDetailView, self).get_context_data(**kwargs)
        groups = ['dietologs','brandowners','trainers', 'main_trainers',]
        self.has_multiple_group(*groups)
        client = self.object
        user = self.request.user
        context['title'] =  'Профиль клиента'
        context['parent_title'] = 'Клиенты'
        context['parent_url'] = reverse_lazy('accounts:client_list')

        ## CHAT
        context['messages'] = reversed(self.get_messages())

        ### FOODPROGRAM ###
        context['foodprogram'] = FoodProgram.objects.filter(client=client).exclude(program__program_type='FG')

        ### ADD OBJECTS ###
        if has_multiple_group(user, ['dietologs','main_trainers','brandowners']):
            context['add_food_program'] = reverse_lazy('accounts:foodprogram_create', kwargs={'slug':client.slug})

        if has_multiple_group(user, ['trainers','main_trainers','brandowners']):
            context['add_workout'] = reverse_lazy('accounts:workout_create', kwargs={'slug':client.slug})

        ### WORKOUTS ###
        context['workouts'] = Workout.objects.filter(client=client)
        ### PROGRESS ###
        context['progress'] = Progress.objects.filter(client=client)
        ### ACTIVITY ###
        context['activity'] = Activity.objects.filter(client=client).order_by('-created')[:50]
        ### NOTES ###
        note = Note.objects.filter(client=client)
        if note.exists():
            context['note_form'] = NoteForm(instance=note[0])
        else:
            context['note_form'] = NoteForm()
        ### ANKETA ###
        context['personal_workout_profile'] = PersonalWorkoutProfileForm(client=client, instance=client.personalworkoutprofile)
        context['personal_nutriment_profile'] = PersonalNutrimentProfileForm(client=client, instance=client.personalnutrimentprofile)
        return context

class ClientNoteUpdateView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, UpdateView):
    model = Note
    form_class = NoteForm

    def get_object(self):
        client_obj = Client.objects.get(slug = self.kwargs['slug'])
        return Note.objects.get_or_create(client=client_obj)[0]


    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_detail', kwargs={'slug':self.kwargs['slug']})

    def get_context_data(self, **kwargs):
        context = super(ClientNoteUpdateView, self).get_context_data(**kwargs)
        groups = ['dietologs','brandowners','trainers', 'main_trainers',]
        self.has_multiple_group(*groups)
        return context


class CountersUpdateView(HasGroupPermissionMixin, FormView):
    form_class = PersonalWorkoutCounter
    second_form_class = PersonalNutrimentCounter
    template_name = 'panel/clients/counters.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_detail', kwargs={'slug':self.kwargs['slug']})

    def get_context_data(self, **kwargs):
        context = super(CountersUpdateView, self).get_context_data(**kwargs)
        groups = ['brandowners','trainers','main_trainers','dietologs']
        self.has_multiple_group(*groups)
        client = Client.objects.get(slug=self.kwargs['slug'])

        # BREADCRUMBS
        context['nutriment_form'] = self.second_form_class
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.kwargs['slug']})
        context['lev2_title'] = client.user.get_full_name()
        context['title'] = 'Добавить программ'
        return context

    def form_valid(self, form):
        try:
            nutriment_form = PersonalNutrimentCounter(self.request.POST)
            if form.is_valid() and nutriment_form.is_valid():
                # WORKOUT
                personal_workout_profile_obj = Client.objects.get(slug=self.kwargs['slug']).personalworkoutprofile
                workout_counter = form.cleaned_data['workout_counter']
                personal_workout_profile_obj.workout_counter += workout_counter
                personal_workout_profile_obj.save(update_fields=["workout_counter"])

                # NUTRIMENT
                personal_nutriment_profile_obj = Client.objects.get(slug=self.kwargs['slug']).personalnutrimentprofile
                nutriment_counter = nutriment_form.cleaned_data['nutriment_counter']
                personal_nutriment_profile_obj.nutriment_counter += nutriment_counter
                personal_nutriment_profile_obj.save(update_fields=["nutriment_counter"])
        except Exception as e:
            logger.exception(e)
        return HttpResponseRedirect(self.get_success_url(self))

class ClientChangeTrainerUpdateView(HasGroupPermissionMixin, IsYourClientPermissionMixin, UpdateView):
    model = Client
    form_class = ClientChangeTrainerForm
    template_name = 'panel/accounts/trainer_form.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_list')

    def get_context_data(self, **kwargs):
        context = super(ClientChangeTrainerUpdateView, self).get_context_data(**kwargs)
        ## CHECK IF NOT USER IN GROUP
        groups = ['brandowners','main_trainers']
        self.has_multiple_group(*groups)
        context['title'] = 'Выбрать тренера'
        context['parent_title'] = 'Клиенты'
        context['parent_url'] = reverse_lazy('accounts:client_list')

        return context

    def get_form_kwargs(self):
        kwargs = super(ClientChangeTrainerUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class ClientDeleteView(HasGroupPermissionMixin, DeleteView):
    model = Client

    def get_context_data(self, **kwargs):
        context = super(ClientDeleteView, self).get_context_data(**kwargs)
        ## CHECK IF NOT USER IN GROUP
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        context['title'] =  'Удаление профиля клиента'
        context['parent_title'] = 'Клиенты'
        context['parent_url'] = reverse_lazy('accounts:client_list')
        return context

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.user.delete()
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


def client_enable(request, pk):
    try:
        group = Group.objects.get(name='brandowners')
        if group not in request.user.groups.all():
            raise Http404
    except Exception as e:
        logger.exception(e)
        if not request.user.is_superuser:
            raise Http404
    qs = Client.objects.get(slug=slug).client_enable()
    obj = Client.objects.get(slug=slug)
    return redirect(obj)

def client_disable(request, pk):
    try:
        group = Group.objects.get(name='brandowners')
        if group not in request.user.groups.all():
            raise Http404
    except Exception as e:
        logger.exception(e)
        if not request.user.is_superuser:
            raise Http404
    qs = Client.objects.get(slug=slug).client_disable()
    obj = Client.objects.get(slug=slug)
    return redirect(obj)

### TRAINERS ###
class TrainerListView(HasGroupPermissionMixin, ListView):
    model = Trainer

    def get_context_data(self, **kwargs):
        context = super(TrainerListView, self).get_context_data(**kwargs)
        ## CHECK IF NOT USER IN GROUP
        groups = ['brandowners','main_trainers']
        self.has_multiple_group(*groups)

        trainer = self.request.user.trainer
        context['object_list'] = trainer.trainer_set.all()
        context['title'] = 'Тренеры'
        context['addobject'] = reverse_lazy('accounts:trainer_create')
        return context


class TrainerCreateView(HasGroupPermissionMixin, CreateView):
    model = User
    form_class = UserCreationForm
    second_form_class = TrainerForm
    template_name = 'panel/accounts/trainer_form.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:trainer_list')

    def get_context_data(self, **kwargs):
        context = super(TrainerCreateView, self).get_context_data(**kwargs)
        ## CHECK IF NOT USER IN GROUP
        groups = ['brandowners','main_trainers']
        self.has_multiple_group(*groups)

        user = self.request.user
        if has_group(user, 'brandowners'):
            context['trainer_form'] = TrainerForm()
        elif has_group(user, 'main_trainers'):
            context['help_trainer_form'] = HelpTrainerForm()
        context['title'] = 'Добавить тренера'
        context['parent_title'] = 'Тренеры'
        context['parent_url'] = reverse_lazy('accounts:trainer_list')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        try:
            help_trainer_form = context.get('help_trainer_form', False)
            trainer_form = context.get('trainer_form', False)
            if trainer_form:
                trainer_form = TrainerForm(self.request.POST, self.request.FILES)
                if form.is_valid() and trainer_form.is_valid():
                    user = form.save()
                    trainer = trainer_form.save(commit=False)
                    main_trainer = self.request.user.trainer
                    trainer.main_trainer = main_trainer
                    trainer.user_id = user.id
                    trainer_group = Group.objects.get(name='main_trainers')
                    trainer_group.user_set.add(user)
                    trainer.save()

            elif help_trainer_form:
                help_trainer_form = HelpTrainerForm(self.request.POST, self.request.FILES)
                if form.is_valid() and help_trainer_form.is_valid():
                    user = form.save()
                    trainer = help_trainer_form.save(commit=False)
                    main_trainer = self.request.user.trainer
                    trainer.main_trainer = main_trainer
                    trainer.user_id = user.id
                    trainer.save()
                    trainer.user.groups.set(help_trainer_form.cleaned_data['group'])

        except Exception as e:
            logger.exception(e)
        return HttpResponseRedirect(self.get_success_url(self))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class TrainerRegisterCreateView(CreateView):
    model = User
    form_class = UserCreationForm
    second_form_class = TrainerForm
    template_name = 'panel/accounts/trainer_register_form.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('custom_login')

    def get_context_data(self, **kwargs):
        context = super(TrainerRegisterCreateView, self).get_context_data(**kwargs)
        context['trainer_form'] = self.second_form_class
        context['title'] = 'Добавить тренера'
        context['parent_title'] = 'Тренеры'
        context['parent_url'] = reverse_lazy('accounts:trainer_list')
        return context

    def form_valid(self, form):
        try:
            trainer_form = TrainerForm(self.request.POST, self.request.FILES)
            if form.is_valid() and trainer_form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                trainer = trainer_form.save(commit=False)
                trainer.user_id = user.id
                trainer_group = Group.objects.get(name='main_trainers')
                trainer_group.user_set.add(user)
                trainer.save()
        except Exception as e:
            logger.exception(e)
        return HttpResponseRedirect(self.get_success_url(self))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))



class TrainerDetailView(HasGroupPermissionMixin, IsYourTrainerPermissionMixin, DetailView):
    model = Trainer

    def get_object(self, queryset=None):
        obj = super(TrainerDetailView, self).get_object(queryset=queryset)
        return obj

    def get_context_data(self, **kwargs):
        context = super(TrainerDetailView, self).get_context_data(**kwargs)
        ## CHECK IF NOT USER IN GROUP
        groups = ['brandowners','main_trainers']
        self.has_multiple_group(*groups)
        context['title'] =  'Профиль тренера'
        context['parent_title'] = 'Тренеры'
        context['parent_url'] = reverse_lazy('accounts:trainer_list')
        return context


class TrainerUpdateView(HasGroupPermissionMixin, UpdateView):
    model = Trainer
    form_class = TrainerForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:trainer_detail', kwargs={"pk":self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(TrainerUpdateView, self).get_context_data(**kwargs)
        ## CHECK IF NOT USER IN GROUP
        groups = ['brandowners',]
        self.has_multiple_group(*groups)
        user = self.request.user
        if has_group(user, 'brandowners'):
            context['form'] = TrainerForm()
        elif has_group(user, 'main_trainers'):
            context['form'] = HelpTrainerForm()
        context['title'] = 'Редактировать профиль тренера'
        context['parent_title'] = 'Тренеры'
        context['parent_url'] = reverse_lazy('accounts:trainer_list')
        return context


class TrainerDeleteView(HasGroupPermissionMixin,  IsYourTrainerPermissionMixin, DeleteView):
    model = Trainer

    def get_context_data(self, **kwargs):
        context = super(TrainerDeleteView, self).get_context_data(**kwargs)
        ## CHECK IF NOT USER IN GROUP
        groups = ['brandowners','main_trainers']
        self.has_multiple_group(*groups)
        context['title'] =  'Удаление профиля тренера'
        context['parent_title'] = 'Тренеры'
        context['parent_url'] = reverse_lazy('accounts:trainer_list')
        return context

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:trainer_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        if self.object.is_boss:
            return HttpResponseRedirect(success_url)

        # MOVE CLIENTS TO MAIN TRAINER
        try:
            if self.object.main_trainer:
                main_trainer = self.object.main_trainer
            else:
                main_trainer = Trainer.objects.get(is_boss=True)

            help_trainers = self.object.trainer_set.all()

            clients = Client.objects.filter(
                Q(trainer=self.object)|
                Q(trainer__in=help_trainers)
                )
            for client in clients:
                client.trainer = main_trainer
                client.save()
        except Exception as e:
            print(e)

        self.object.delete()
        return HttpResponseRedirect(success_url)


def trainer_enable(request, pk):
    try:
        groups = ['brandowners','main_trainers']
        if not Group.pbjects.filter(name__in=groups).exists():
            raise Http404
    except Exception as e:
        logger.exception(e)

    obj = Trainer.objects.get(id=pk)
    qs = obj.trainer_enable()
    return redirect(obj)

def trainer_disable(request, pk):
    try:
        groups = ['brandowners','main_trainers']
        if not Group.pbjects.filter(name__in=groups).exists():
            raise Http404
    except Exception as e:
        logger.exception(e)

    obj = Trainer.objects.get(id=pk)
    qs = obj.trainer_disable()
    return redirect(obj)


########################################################################################################################
## FOODPROGRAM CRUD

class FoodProgramCreateView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, PersonalFoodProgramExist, CreateView):
    model = FoodProgram
    form_class = FoodProgramForm

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.client = self.get_client()
        instance.program = Program.objects.get(program_type='FP')
        instance.save()
        i = 0
        for day in SettingsDay.objects.all():
            Day.objects.create(name=day, foodprogram=instance, sorting=i)
            i+=1
        return super(FoodProgramCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FoodProgramCreateView, self).get_context_data(**kwargs)
        ## CHECK IF NOT USER IN GROUP
        groups = ['brandowners','main_trainers','dietologs',]
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev3_title'] = 'Программы питания'
        context['title'] = 'Добавить программу питания'
        return context


class FoodProgramCloneCreateView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, CreateView):
    model = FoodProgram
    form_class = FoodProgramCloneForm

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})

    def form_valid(self, form):
        foodprogramclone_obj = form.save(commit=False)

        # GET CURRENT FOODPROGRAM OBJ
        current_foodprogram_id = self.kwargs['pk']
        current_foodprogram_obj = FoodProgram.objects.get(id=self.kwargs['pk'])

        # CLONE CURRENT FOODPROGRAM OBJ
        foodprogramclone_obj.name = current_foodprogram_obj.name
        foodprogramclone_obj.content = current_foodprogram_obj.content
        foodprogramclone_obj.program = current_foodprogram_obj.program
        foodprogramclone_obj.save()

        # CLONE DAYS OF CURRENT FOODPROGRAM
        for i in current_foodprogram_obj.day_set.all():
            day_kwargs = {}
            day_kwargs['foodprogram'] = foodprogramclone_obj
            day_kwargs['name'] = i.name
            day_kwargs['sorting'] = i.sorting
            day_obj = Day.objects.create(**day_kwargs)

            # CLONE TIMES OF CURRENT DAY OF CURRENT FOODPROGRAM
            for x in i.time_set.all():
                time_kwargs = {}
                time_kwargs['settingstime'] = x.settingstime
                time_kwargs['day'] = day_obj
                time_kwargs['weight'] = x.weight
                time_kwargs['kkal'] = x.kkal
                time_kwargs['protein'] = x.protein
                time_kwargs['fat'] = x.fat
                time_kwargs['carbohydrate'] = x.carbohydrate
                time_obj = Time.objects.create(**time_kwargs)

                # CLONE FOOD OF TIMES OF CURRENT DAY OF CURRENT FOODPROGRAM
                for y in x.food_set.all():
                    food_kwargs = {}
                    food_kwargs['foodprogram'] = foodprogramclone_obj
                    food_kwargs['day'] = day_obj
                    food_kwargs['time'] = x
                    food_kwargs['product'] = y.product
                    food_kwargs['weight'] = y.weight
                    food_kwargs['kkal'] = y.kkal
                    food_kwargs['protein'] = y.protein
                    food_kwargs['fat'] = y.fat
                    food_kwargs['carbohydrate'] = y.carbohydrate
                    food_obj = Food.objects.create(**food_kwargs)
        return super(FoodProgramCloneCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FoodProgramCloneCreateView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','dietologs','main_trainers']
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev3_title'] = 'Программы питания'
        context['title'] = 'Клонировать программу питания'
        return context

    def get_form_kwargs(self):
        kwargs = super(FoodProgramCloneCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class FoodProgramDetailView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, DetailView):
    model = FoodProgram

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_object(self, queryset=None):
        obj = super(FoodProgramDetailView, self).get_object(queryset=queryset)
        return obj

    def get_context_data(self,  **kwargs):
        context = super(FoodProgramDetailView, self).get_context_data(**kwargs)
        context['days'] = Day.objects.filter(foodprogram=self.get_object())
        context['title'] = '%s' % self.get_object().name

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','dietologs','main_trainers']
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev3_title'] = 'Программы питания'
        context['title'] = self.get_object().name

        context['foodform'] = FoodForm
        context['timeform'] = TimeForm
        context['client'] = self.get_client()
        return context


class FoodProgramUpdateView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, UpdateView):
    model = FoodProgram
    form_class = FoodProgramForm

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})

    def get_context_data(self, **kwargs):
        context = super(FoodProgramUpdateView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','dietologs','main_trainers']
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev3_title'] = 'Программы питания'
        context['title'] = '{} от {}'.format(self.object.name, self.object.created)
        return context


class FoodProgramDeleteView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, DeleteView):
    model = FoodProgram

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_object(self, queryset=None):
        obj = super(FoodProgramDeleteView, self).get_object(queryset=queryset)
        return obj

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})

    def get_context_data(self, **kwargs):
        context = super(FoodProgramDeleteView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','dietologs','main_trainers']
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev3_title'] = 'Программы питания'
        context['title'] = 'Удалить программу питания {} от {}'.format(self.object.name, self.object.created)
        return context

######################################################################################################################
## FOOD CRUD

def json_product_list(request):
    data = {}
    if not has_groups(['brandowners','dietologs','main_trainers'], request):
        return JsonResponse({"suggestions":[{'value':'', 'data':''}]})

    if request.is_ajax():
        q = request.GET.get('query', '')
        query = make_query(q)
        products = Product.objects.filter(query)[:20]
        suggestions = []
        for product in products:
            product_weight = product.kbzu_100g.weight
            kkal, protein, fat, carbohydrate = product.kbzu_100g.kkal, product.kbzu_100g.protein, product.kbzu_100g.fat, product.kbzu_100g.carbohydrate
            product_name = '{0} ({1}г | К: {2} | Б: {3} | Ж: {4} | У: {5})'.format(product.name,product_weight, kkal, protein, fat, carbohydrate)

            if product.product_meal == 'M':
                product_weight = product.kbzu_1portion.weight
                kkal, protein, fat, carbohydrate = product.kbzu_1portion.kkal, product.kbzu_1portion.protein, product.kbzu_1portion.fat, product.kbzu_1portion.carbohydrate
                product_name = '{0} (1 порция: {1}г | К: {2} | Б: {3} | Ж: {4} | У: {5})'.format(product.name,product_weight, kkal, protein, fat, carbohydrate)
            suggestions.append({ "value": product_name, "data": { 'category': product.category, 'product_id':product.id }})
        data = {"suggestions":suggestions}
    else:
        data = 'fail'
    return JsonResponse(data)

def food_create(request, *args, **kwargs):
    if not has_groups(['brandowners','dietologs','main_trainers'], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        foodform  =  FoodForm(request.POST)
        timeform = TimeForm(request.POST)
        if foodform.is_valid() and timeform.is_valid():

            # GET DATA FROM FORM
            settingstime = timeform.cleaned_data['settingstime']
            settingstime_obj = SettingsTime.objects.get(name=str(settingstime.name)[:-3])
            foodprogram_obj = FoodProgram.objects.get(id=int(request.POST.get('foodprogram', False)))
            day_obj = Day.objects.get(id=int(request.POST.get('day', False)))
            product_obj = Product.objects.get(id=int(request.POST.get('product_id', False)))


            # CREATE TIME AND FOOD OBJ
            try:
                time_obj, created = Time.objects.get_or_create(settingstime=settingstime, day=day_obj)
                food_obj = foodform.save(commit=False)
                food_obj.foodprogram = foodprogram_obj
                food_obj.day = day_obj
                food_obj.time = time_obj
                food_obj.product = product_obj

                # UPDATE KBZU 100g
                food_obj.kkal = food_obj.product.kbzu_100g.kkal/100*food_obj.weight
                food_obj.protein = food_obj.product.kbzu_100g.protein/100*food_obj.weight
                food_obj.fat = food_obj.product.kbzu_100g.fat/100*food_obj.weight
                food_obj.carbohydrate = food_obj.product.kbzu_100g.carbohydrate/100*food_obj.weight
                product_unit = food_obj.product.kbzu_100g.weight

                # UPDATE KBZU 1PORTION
                if product_obj.recipe:
                    food_obj.kkal = food_obj.product.kbzu_1portion.kkal/food_obj.product.kbzu_1portion.weight*food_obj.weight
                    food_obj.protein = food_obj.product.kbzu_1portion.protein/food_obj.product.kbzu_1portion.weight*food_obj.weight
                    food_obj.fat = food_obj.product.kbzu_1portion.fat/food_obj.product.kbzu_1portion.weight*food_obj.weight
                    food_obj.carbohydrate = food_obj.product.kbzu_1portion.carbohydrate/food_obj.product.kbzu_1portion.weight*food_obj.weight
                    product_unit = food_obj.product.kbzu_1portion.weight
                food_obj.save()
            except Exception as e:
                logger.exception(e)

            data = {
                    'food_id': food_obj.id,
                    'food_delete': reverse_lazy("accounts:food_delete"),
                    'product_unit': product_unit,
                    'eattime_id': time_obj.id,
                    'product': food_obj.product.name,
                    'weight': food_obj.weight,
                    'time': settingstime_obj.name,
                    'kkal': food_obj.kkal,
                    'protein': food_obj.protein,
                    'fat': food_obj.fat,
                    'carbohydrate': food_obj.carbohydrate,
                    'time_weight': time_obj.weight,
                    'time_kkal': time_obj.kkal,
                    'time_protein': time_obj.protein,
                    'time_fat': time_obj.fat,
                    'time_carbohydrate': time_obj.carbohydrate,
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


def food_delete(request, *args, **kwargs):
    if not has_groups(['brandowners','dietologs','main_trainers'], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        food_id = request.POST.get('food', False)
        eattime_id = request.POST.get('eattime', False)
        row_delete = request.POST.get('row_delete', False)
        eattime_delete = request.POST.get('eattime_delete', False)
        food_obj = Food.objects.get(id=food_id)
        time_obj = Time.objects.get(id=eattime_id)
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

########################################################################################################################
## WORKOUT CRUD

class WorkoutCreateView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, PersonalWorkoutProgramExist, CreateView):
    model = Workout
    form_class = WorkoutForm

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.client = self.get_client()
        instance.program = Program.objects.get(program_type='WP')
        instance.save()
        settings_rest_time_default = SettingsRestTime.objects.all()[1]
        Wset.objects.create(number=1, workout=instance, rest_time=settings_rest_time_default, approach_number=3)
        return super(WorkoutCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(WorkoutCreateView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','trainers','main_trainers']
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev3_title'] = 'Программы тренировок'
        context['title'] = 'Добавить программу тренировок'
        return context


class WorkoutCloneCreateView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, CreateView):
    model = Workout
    form_class = WorkoutCloneForm

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})


    def form_valid(self, form):
        clone_workout_obj = form.save(commit=False)

        # GET CURRENT WORKOUT OBJ
        current_workout_id = self.kwargs['pk']
        current_workout_obj = Workout.objects.get(id=self.kwargs['pk'])

        # CLONE CURRENT WORKOUT
        clone_workout_obj.name = current_workout_obj.name
        clone_workout_obj.content = current_workout_obj.content
        clone_workout_obj.program = current_workout_obj.program
        clone_workout_obj.is_finished = current_workout_obj.is_finished
        clone_workout_obj.save()

        # CLONE SETS OF CURRENT WORKOUT
        for i in current_workout_obj.wset_set.all():
            wset_kwargs = {}
            wset_kwargs['workout'] = clone_workout_obj
            wset_kwargs['number'] = i.number
            wset_kwargs['datainput'] = i.datainput
            wset = Wset.objects.create(**wset_kwargs)

            # CLONE TRAININGS OF SETS OF CURRENT WORKOUT
            for x in i.training_set.all():
                wset_training_kwargs = {}
                wset_training_kwargs['workout'] = clone_workout_obj
                wset_training_kwargs['wset'] = wset
                wset_training_kwargs['exercise'] = x.exercise
                wset_training_kwargs['exercise_input'] = x.exercise_input
                wset_training_kwargs['content'] = x.content
                wset_training_kwargs['rest_time'] = x.rest_time
                training = Training.objects.create(**wset_training_kwargs)

        return super(WorkoutCloneCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(WorkoutCloneCreateView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','trainers','main_trainers']
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev3_title'] = 'Программы тренировок'
        context['title'] = 'Клонировать программу тренировок'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkoutCloneCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class WorkoutDetailView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, DetailView):
    model = Workout

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_object(self, queryset=None):
        obj = super(WorkoutDetailView, self).get_object(queryset=queryset)
        return obj

    def get_context_data(self,  **kwargs):
        context = super(WorkoutDetailView, self).get_context_data(**kwargs)
        context['wsets'] = Wset.objects.filter(workout=self.get_object())
        context['trainingform'] = TrainingForm
        context['exercise_filter_form'] = ExerciseFilterForm
        context['training_template_form'] = TrainingTemplateForm
        context['addwset'] = reverse_lazy('accounts:wset_create', kwargs={'slug':self.kwargs['slug'], 'pk':self.kwargs['pk']})
        context['client'] = self.get_client()

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','trainers','main_trainers']
        self.has_multiple_group(*groups)
        client = self.get_client()

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':client.slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':client.slug})
        context['lev3_title'] = 'Программы тренировок'
        context['title'] = '%s' % self.get_object().name
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkoutDetailView, self).get_form_kwargs()
        kwargs.update({'workout_id': self.get_object().id})
        return kwargs


class WorkoutUpdateView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, UpdateView):
    model = Workout
    form_class = WorkoutForm

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})

    def get_context_data(self, **kwargs):
        context = super(WorkoutUpdateView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','trainers','main_trainers']
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev3_title'] = 'Программы тренировок'
        context['title'] = 'Редактировать тренировку от %s' % self.object.created
        return context


class WorkoutDeleteView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, DeleteView):
    model = Workout

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_object(self, queryset=None):
        obj = super(WorkoutDeleteView, self).get_object(queryset=queryset)
        return obj

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})

    def get_context_data(self, **kwargs):
        context = super(WorkoutDeleteView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','trainers','main_trainers']
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev3_title'] = 'Программы тренировок'
        context['title'] = 'Редактировать тренировку от %s' % self.object.created
        return context

######################################################################################################################
## TRAINING AJAX

def json_exercisecomment_detail(request):
    if not has_groups(['brandowners','trainers','main_trainers'], request):
        return JsonResponse({})

    if request.is_ajax():
        exercise_id = request.GET.get('exercise_id', '')
        client_id = request.GET.get('client_id', '')
        workout_id = request.GET.get('workout_id', '')
        # GET LAST TRAINING OBJ WITH CHOSEN EXERCISE
        try:
            training_obj = Training.objects.filter(workout__client__id=client_id, exercise__id=exercise_id).last()
            if training_obj:
                training_obj_content = training_obj.content
                training_obj_time = training_obj.rest_time.id
            else:
                training_obj_content = ''
                training_obj_time = ''
        except Exception as e:
            logger.exception(e)

        try:
            # GET EXERCISE COMMENT OBJECT AND ITS DATA
            exercise_comment_obj = ExerciseComment.objects.filter(client__id=client_id, exercise__id=exercise_id).last()
            if exercise_comment_obj != None:
                exercise_comment_name_id = exercise_comment_obj.name_id
                exercise_comment_workout = exercise_comment_obj.workout.name
                exercise_comment_exercise = exercise_comment_obj.exercise.name
                exercise_comment_created = exercise_comment_obj.created
                exercise_comment_content = exercise_comment_obj.content

                # GET EXERCISE COMMENT NAME
                exercise_comment_name = ExerciseCommentName.objects.get(name_id=exercise_comment_name_id).name

                # GET TRAINING OF THAT EXERCISE

                data = {
                'exercise_comment_workout':exercise_comment_workout,
                'exercise_comment_exercise':exercise_comment_exercise,
                'exercise_comment_created':exercise_comment_created,
                'exercise_comment_name':exercise_comment_name,
                'exercise_comment_content':exercise_comment_content,
                'training_obj_content':training_obj_content,
                'training_obj_time':training_obj_time
            }
                return JsonResponse(data)

        except Exception as e:
            logger.exception(e)

        data = {
            'exercise_comment_name':'',
            'training_obj_content':training_obj_content,
            'training_obj_time':training_obj_time,
        }
        return JsonResponse(data)

    else:
        data = 'fail'
    return JsonResponse(data)

def make_query(q, content_owner_obj=None):
    query = Q()
    if content_owner_obj is not None:
        query &= Q(content_owner=content_owner_obj)
    query &= Q(name__icontains=q)
    return query

def json_personal_exercise_list(request):
    data = {}
    if not has_groups(['brandowners','trainers','main_trainers'], request):
        return JsonResponse({"suggestions":[{'value':'', 'data':''}]})

    if request.is_ajax():
        q = request.GET.get('query', '')
        main_content_owner_obj = Trainer.objects.get(is_boss=True)
        workout_id = request.GET.get('workout_id', None)
        if workout_id != None:
            workout_obj = Workout.objects.get(id=workout_id)
            if workout_obj.self_content:
                content_owner_obj = workout_obj.client.trainer
            else:
                content_owner_obj = main_content_owner_obj
        else:
            content_owner_obj = main_content_owner_obj

        query = make_query(q)
        # query = make_query(q, content_owner_obj)
        exercises = Exercise.objects.filter(query)[:10]
        suggestions = []
        for exercise in exercises:
            content_owner = exercise.content_owner.user.get_full_name()
            suggestions.append({ "value": exercise.name, "data": {'content_owner':content_owner, 'exercise_id':exercise.id}})
            # suggestions.append({ "value": exercise.name, "data": exercise.id})
        data = {"suggestions":suggestions}
    else:
        data = 'fail'
    return JsonResponse(data)


def get_filter_exercise(workout_occupation, model_sex, main_muscle, reset=None):
    query = Q()
    if workout_occupation != None:
        query &= Q(workout_occupation__id=workout_occupation)
    if model_sex != None:
        query &= Q(model_sex__id=model_sex)
    if main_muscle != None:
        query &= Q(main_muscle__id=main_muscle)

    if reset:
        qs = Exercise.objects.all()
    else:
        qs = Exercise.objects.filter(query).distinct()

    # GATHERING EVERYTHING IN DICTS
    filter_exercise_dct = {}
    workout_occupation_dct = {}
    model_sex_dct = {}
    main_muscle_dct = {}
    current_selected = {
        'workout_occupation':workout_occupation if workout_occupation != None else '',
        'model_sex':model_sex if model_sex != None else '',
        'main_muscle':main_muscle if main_muscle != None else '',
    }

    for item in qs:
        try:
            filter_exercise_dct[item.id] = item.name
            workout_occupation_dct[item.workout_occupation.id] = item.workout_occupation.name
            model_sex_dct[item.model_sex.id] = item.model_sex.name
            main_muscle_dct[item.main_muscle.id] = item.main_muscle.content
        except:
            continue

    return (filter_exercise_dct, workout_occupation_dct, model_sex_dct, main_muscle_dct, current_selected)

def get_request_data_or_none(request, param):
    s = request.GET.get(param, '')
    return int(s) if s != '' else None

def filter_exercise_list(request):
    data = {}
    if not has_groups(['brandowners','trainers','main_trainers'], request):
        return JsonResponse(data)

    if request.is_ajax():
        workout_occupation = get_request_data_or_none(request, 'workout_occupation')
        model_sex = get_request_data_or_none(request, 'model_sex')
        main_muscle = get_request_data_or_none(request, 'main_muscle')
        if request.GET.get('reset', False) == 'reset':
            filter_exercise, workout_occupation, model_sex, main_muscle, current_selected = get_filter_exercise(workout_occupation, model_sex, main_muscle, reset=True)
        else:
            filter_exercise, workout_occupation, model_sex, main_muscle, current_selected = get_filter_exercise(workout_occupation, model_sex, main_muscle)

        data = {
        'exercises':filter_exercise,
        'workout_occupation':workout_occupation,
        'model_sex':model_sex,
        'main_muscle':main_muscle,
        'current_selected':current_selected,
        }

    return JsonResponse(data)


class WsetCreateView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, CreateView):
    model = Wset
    form_class = WsetForm

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:workout_detail', kwargs={'slug':self.kwargs['slug'], 'pk':self.kwargs['pk']})

    def form_valid(self, form):
        wset_obj = form.save(commit=False)
        workout_obj = Workout.objects.get(id=self.kwargs['pk'])
        new_wset_number = workout_obj.wset_set.all().count() + 1
        wset_obj.number = new_wset_number
        wset_obj.workout = workout_obj
        wset_obj.save()
        return super(WsetCreateView, self).form_valid(form)

    def get_context_data(self,  **kwargs):
        context = super(WsetCreateView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','trainers', 'main_trainers']
        self.has_multiple_group(*groups)

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':self.get_client().slug})
        context['lev3_title'] = 'Программы тренировок'
        context['title'] = 'Добавить новый сет'
        context['button'] = 'Добавить сет'

        return context


class WsetUpdateView(HasGroupPermissionMixin, ClientOwnerPermissionMixin, UpdateView):
    model = Wset
    form_class = WsetForm

    def get_client(self):
        return Client.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:workout_detail', kwargs={'slug':self.kwargs['slug'], 'pk':self.kwargs['sk']})


    def get_context_data(self,  **kwargs):
        context = super(WsetUpdateView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners','trainers', 'main_trainers']
        self.has_multiple_group(*groups)
        obj = self.get_object()
        client = self.get_client()

        # BREADCRUMBS
        context['lev1_url'] = reverse_lazy('accounts:client_list')
        context['lev1_title'] = 'Клиенты'
        context['lev2_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':client.slug})
        context['lev2_title'] = self.get_client().user.get_full_name()
        context['lev3_url'] = reverse_lazy('accounts:client_detail', kwargs={'slug':client.slug})
        context['lev3_title'] = 'Программы тренировок'
        context['title'] = 'Редактирование сета №{0}'.format(obj.number, **kwargs)
        context['button'] = 'Редактировать'
        return context


def training_create(request, *args, **kwargs):
    if not has_groups(['brandowners','trainers','main_trainers'], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        trainingform = TrainingForm(request.POST)
        if trainingform.is_valid():
            # GET DATA FROM FORM
            content = request.POST.get('content', False)
            workout_obj = Workout.objects.get(id=int(request.POST.get('workout', False)))
            wset_obj = Wset.objects.get(id=int(request.POST.get('wset', False)))
            exercise_id = int(request.POST.get('exercise', False))
            exercise_obj = Exercise.objects.get(id=exercise_id)

            # CREATE TRAINING OBJ
            training_obj = trainingform.save(commit=False)
            training_obj.workout = workout_obj
            training_obj.content = content
            training_obj.wset = wset_obj
            training_obj.exercise = exercise_obj
            training_obj.save()


            data = {
                    'training': training_obj.id,
                    'training_delete': reverse_lazy("accounts:training_delete"),
                    'workout': workout_obj.id,
                    'wset': wset_obj.id,
                    'excercise': training_obj.exercise.name,
                    'content': training_obj.content,
                    'rest_time': training_obj.rest_time.name,
                        }

            return JsonResponse(data)

        else:
            data = {
                    'Form errors': trainingform.errors
                        }
            return JsonResponse(data)
    else:
        trainingform = TrainingForm(prefix = 'TrainingForm')
        data = {
                'message': "There is an error."
                    }
        return JsonResponse(data)


def training_delete(request, *args, **kwargs):
    if not has_groups(['brandowners','trainers','main_trainers'], request):
        return JsonResponse({})

    if request.method == 'POST' and request.is_ajax():
        training_obj = Training.objects.get(id=int(request.POST.get('training', False)))
        training_obj.delete()
        data = {
                'training': training_obj.id,
                    }
        return JsonResponse(data)
    else:
        data = {
                'message': "There is an error."
                    }
        return JsonResponse(data)

########################################################################################################################
## LEAD CHAT

## CREATE NEW LEADUSER

class LeadUserListView(HasGroupPermissionMixin, ListView):
    model = LeadUser
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super(LeadUserListView, self).get_context_data(**kwargs)
        context['title'] = 'Лиды'

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        # context['object_list'] = sorted(self.get_queryset(), key=lambda x: x.unread_by_trainer_messages(), reverse=True)
        return context


class LeadUserDetailView(HasGroupPermissionMixin, LeadUserPermissionMixin, DetailView):
    model = LeadUser

    def get_object(self, queryset=None):
        obj = super(LeadUserDetailView, self).get_object(queryset=queryset)
        if queryset is None:
            queryset = self.get_queryset()
        try:
            obj = queryset.get(pk=self.kwargs.get('pk', None))
        except ObjectDoesNotExist as e:
            raise Http404
        return obj

    def get_messages(self, *args, **kwargs):
        leaduser_obj = self.get_object()
        leaduser_obj.new_messages_from_client = False
        leaduser_obj.save()
        messages = ChatMessage.objects.none()
        trainer = Trainer.objects.get(is_boss=True)
        thread_qs = Thread.objects.filter(leaduser=leaduser_obj, trainer=trainer)
        if thread_qs.exists():
            thread_obj = thread_qs[0]
            messages = thread_obj.chatmessage_set.order_by('-timestamp')[:50]
        return messages

    def get_context_data(self, **kwargs):
        context = super(LeadUserDetailView, self).get_context_data(**kwargs)

        # CHECK IF NOT USER IN GROUP
        groups = ['brandowners',]
        self.has_multiple_group(*groups)

        context['messages'] = reversed(self.get_messages())
        context['title'] = 'Лид № {} от {}'.format(self.get_object().id, self.get_object().created)
        context['parent_title'] = 'Лиды'
        context['parent_url'] = reverse_lazy('accounts:leaduser_list')
        return context


def leaduser_enable(request, pk, chatid):
    if not request.user.is_authenticated:
        raise Http404

    if not request.user.is_superuser:
        try:
            group = Group.objects.get(name='brandowners')
            if group not in request.user.groups.all():
                raise Http404
        except Exception as e:
            logger.exception(e)
            raise Http404
    leaduser_obj = LeadUser.objects.get(id=pk).remove_ban_user()
    return redirect(reverse_lazy('accounts:leaduser_detail', kwargs={'pk':pk, 'chatid':chatid}))

def leaduser_disable(request, pk, chatid):
    if not request.user.is_authenticated:
        raise Http404

    if not request.user.is_superuser:
        try:
            group = Group.objects.get(name='brandowners')
            if group not in request.user.groups.all():
                raise Http404
        except Exception as e:
            logger.exception(e)
            raise Http404
    leaduser_obj = LeadUser.objects.get(id=pk).ban_user()
    return redirect(reverse_lazy('accounts:leaduser_detail', kwargs={'pk':pk, 'chatid':chatid}))



################### FOOD RECIPES FOR INSTAGRAM ####################
def get_week_day(today):
    day_value = str(date.weekday(today))
    days = {
        '0':'Понедельник',
        '1':'Вторник',
        '2':'Среда',
        '3':'Четверг',
        '4':'Пятница',
        '5':'Суббота',
        '6':'Воскресенье',
    }
    return days[day_value]

class ClientFoodRecipesTemplateView(TemplateView):
    template_name = 'insta/recipes.html'

    def get_context_data(self, **kwargs):
        context = super(ClientFoodRecipesTemplateView, self).get_context_data(**kwargs)
        kkal_value = self.request.GET.get('kkal',None)
        if kkal_value is not None:
            min_kkal = int(kkal_value) - int(kkal_value)/10
            max_kkal = int(kkal_value) + int(kkal_value)/10
            pp_days = Day.objects.filter(day_kbzu__range=[min_kkal,max_kkal])[:2]
        foodprograms_qs = FoodProgram.objects.all()
        week_day = get_week_day(today)
        # pp_days = Day.objects.filter(foodprogram__client__user__username='nikakoss1', name=week_day)|Day.objects.filter(foodprogram__client__user__username='nikakoss23', name=week_day)
        context['title'] = 'ПП Меню и рецепты на {0}'.format(today)
        context['days'] = pp_days
        # context['day'] = week_day
        return context


class ClientFoodRecipesCleanTemplateView(TemplateView):
    template_name = 'insta/recipes_clean.html'

    def get_context_data(self, **kwargs):
        context = super(ClientFoodRecipesCleanTemplateView, self).get_context_data(**kwargs)
        kkal_value = self.request.GET.get('kkal',None)
        if kkal_value is not None:
            min_kkal = int(kkal_value) - int(kkal_value)/10
            max_kkal = int(kkal_value) + int(kkal_value)/10
            pp_days = Day.objects.filter(day_kbzu__range=[min_kkal,max_kkal])[:1]
        foodprograms_qs = FoodProgram.objects.all()
        week_day = get_week_day(today)
        # pp_days = Day.objects.filter(foodprogram__client__user__username='nikakoss1', name=week_day)|Day.objects.filter(foodprogram__client__user__username='nikakoss23', name=week_day)
        context['title'] = 'ПП Меню и рецепты на {0}'.format(today)
        context['days'] = pp_days
        # context['day'] = week_day
        return context


class BotFoodRecipesCleanTemplateView(TemplateView):
    template_name = 'insta/recipes_bot.html'
    random_tags = [
        '#фитнес #мотивация #правильноепитание #тренировка #худеемвместе #тренер #похудение #здоровыйобразжизни #тренировки #яхудею #худеем #фитнесс #жируходи #кроссфит #спортэтожизнь #персональныйтренер #качалка #тренажерныйзал #худеювинста #фитнестренер #дневникпп #наспорте #дневникпохудения','#будустройной #красотаиздоровье #какпохудеть #силаволи #худеемправильно #спортивноетело #худеемклету #будьвформе #худеюклету #спортсила #фитнесмотивация #стройность #красиваяфигура #трансформация #зожификация #красивыелюди #стройноетело #работанадсобой #жирунет #спортлайф #силадуха #житьздорово #жир','#фитнесдома #спортрежим #спортивнаяфигура #жирубой #лучшевсех #похудела #спортивная #спортивные #спортдлявсех #фитнеспитание #спортвмассы #дневникхудеющей #всемспорт #лишнийвес #фитнесцентр #худеюправильно #персональныетренировки #фитнесдневник #спортжизнь #япохудею #снижениевеса #будьтездоровы #худеемвинста','#фитнесхаус #здоровьеикрасота #теломечты #здоровоетело #тренера #спортспортспорт #сушкатела #стройнаяфигура #мотивацияспорт #ялюблюспорт #самосовершенствование #хочубытьстройной #похудею #жиросжигание #мотивациякаждыйдень #жиросжигание #похудетьбыстро #худеемлегко #мотивациякпохудению #спортивнаяжизнь #жиротоп #будухудой #фитнесблог','#правильноепохудение #жиротопка #худеемпослеродов #фитнеспроект #трансформациятела #мотивациянакаждыйдень #спортмотивация #здороваясемья #похудениедоипосле #похудениебездиет'
    ]

    def get_context_data(self, **kwargs):
        context = super(BotFoodRecipesCleanTemplateView, self).get_context_data(**kwargs)
        kkal_value = self.request.GET.get('kkal',None)
        if kkal_value is not None:
            min_kkal = int(kkal_value) - int(kkal_value)/10
            max_kkal = int(kkal_value) + int(kkal_value)/10
            pp_days = Day.objects.filter(day_kbzu__range=[min_kkal,max_kkal])
        foodprograms_qs = FoodProgram.objects.all()
        week_day = get_week_day(today)
        context['title'] = 'ПП Меню и рецепты на {0}'.format(today)
        context['days'] = pp_days
        context['tags'] = random.choice(self.random_tags)
        return context


class BotWorkoutCleanTemplateView(TemplateView):
    template_name = 'insta/workouts_bot.html'
    random_tags = [
        '#фитнес #мотивация #правильноепитание #тренировка #худеемвместе #тренер #похудение #здоровыйобразжизни #тренировки #яхудею #худеем #фитнесс #жируходи #кроссфит #спортэтожизнь #персональныйтренер #качалка #тренажерныйзал #худеювинста #фитнестренер #дневникпп #наспорте #дневникпохудения','#будустройной #красотаиздоровье #какпохудеть #силаволи #худеемправильно #спортивноетело #худеемклету #будьвформе #худеюклету #спортсила #фитнесмотивация #стройность #красиваяфигура #трансформация #зожификация #красивыелюди #стройноетело #работанадсобой #жирунет #спортлайф #силадуха #житьздорово #жир','#фитнесдома #спортрежим #спортивнаяфигура #жирубой #лучшевсех #похудела #спортивная #спортивные #спортдлявсех #фитнеспитание #спортвмассы #дневникхудеющей #всемспорт #лишнийвес #фитнесцентр #худеюправильно #персональныетренировки #фитнесдневник #спортжизнь #япохудею #снижениевеса #будьтездоровы #худеемвинста','#фитнесхаус #здоровьеикрасота #теломечты #здоровоетело #тренера #спортспортспорт #сушкатела #стройнаяфигура #мотивацияспорт #ялюблюспорт #самосовершенствование #хочубытьстройной #похудею #жиросжигание #мотивациякаждыйдень #жиросжигание #похудетьбыстро #худеемлегко #мотивациякпохудению #спортивнаяжизнь #жиротоп #будухудой #фитнесблог','#правильноепохудение #жиротопка #худеемпослеродов #фитнеспроект #трансформациятела #мотивациянакаждыйдень #спортмотивация #здороваясемья #похудениедоипосле #похудениебездиет'
    ]

    def get_context_data(self, **kwargs):
        context = super(BotWorkoutCleanTemplateView, self).get_context_data(**kwargs)
        context['workouts'] = self.get_workouts()
        context['tags'] = random.choice(self.random_tags)
        return context

    def get_workouts(self):
        daily_program = Program.objects.get(daily=True)
        return daily_program.workout_set.all()

























