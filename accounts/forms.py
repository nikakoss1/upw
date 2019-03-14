# -*- coding: utf-8 -*-
from .models import Client, Trainer, Progress, Food, FoodProgram, Time, Workout, Wset, Training, LeadUser, Note, PersonalNutrimentProfile, PersonalWorkoutProfile
from appsettings.mixins import ClientOwnerPermissionMixin, has_group
from captcha.fields import ReCaptchaField
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, ButtonHolder, Submit, Field
from django import forms
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.safestring import mark_safe
import re
from options.models import Exercise


#############################################################################################################################
## HELP FUNC

def file_size(value): # add this to some file where you can import it from
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Файл слишком большой, размер не должен превышать 2МБ.')

def has_latin(text):
    return bool(re.search('[a-zA-Z]', text))

#############################################################################################################################
## LEADUSERS

class LeadUserForm(forms.ModelForm):
    class Meta:
        model = LeadUser
        fields = ['uuid', 'is_banned']

#############################################################################################################################
## CLIENTS
## Client registration


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'patronymic',
            'age',
            'high',
            'weight',
            'wish_weight',
            'sex',
            'training_level',
            'oferta',
            'konf',
        ]
        labels = {
            'patronymic':'Отчество',
            'phone':'Телефон',
            'age':'Возраст',
            'weight':'Текущий вес (кг)',
            'wish_weight':'Желаемый вес (кг)',
            'high':'Рост (см)',
            'sex':'Пол',
            'training_level':'Уровень физической активности',
        }


    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            )
        self.fields['oferta'].label = '<a href="{0}" target="_blank">С условиями оферты согласен(-а)</a>'.format('/static/oferta.pdf')
        self.fields['konf'].label = '<a href="/static/konf.pdf" target="_blank">С условиями политики конфиденциальности согласен(-а)'


class ClientChangeTrainerForm(forms.ModelForm):

    trainer = forms.ModelChoiceField(label='Выберите тренера', queryset=Trainer.objects.all())
    class Meta:
        model = Client
        fields = ['trainer']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        trainer = request.user.trainer
        trainer_qs = Trainer.objects.filter(id=trainer.id)
        qs = trainer.trainer_set.all()
        super(ClientChangeTrainerForm, self).__init__(*args, **kwargs)
        self.fields['trainer'].queryset = trainer_qs|qs



class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']
        labels = {
            'content':'Любые заметки'
        }

    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            )



#############################################################################################################################
## PROGRESS

class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['image1','image2','image3','current_weight','chest','waistline','hip','leg']
        labels = {
            'image1':'Спереди',
            'image2':'Сбоку',
            'image3':'Сзади',
            'current_weight':'Текущий вес',
            'chest':'Объем груди',
            'waistline':'Объем талии',
            'hip':'Объем бедер',
            'leg':'Объем ноги',
        }

#############################################################################################################################
## TRAINERS
## TRAINER REGISTER

class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = [
            'avatar',
            'city',
            'phone',
            'image1',
            'image2',
            'image3',
            'image4',
            'image5',
            'image6',
            'whatsapp',
            'mail',
            'vk',
            'ok',
            'instagram',
            'fb',
            'yt',
            'promo_video',
        ]
        labels = {
            'avatar':'Аватар',
            'phone':'Телефон',
            'contact_email':'Контактный имейл для клиентов',
            'whatsapp':'WhatsApp',
            'vk':'ВКонтакте',
            'ok':'Одноклассники',
            'instagram':'Инстаграм',
            'fb':'Фейсбук',
            'yt':'Youtube',
            'promo_video':'Промо видео на ютубе',
            'desc':'Дополнительно',
            'content':'Любая дополнительная информация',
            'image1':'Изображение №1',
            'image2':'Изображение №2',
            'image3':'Изображение №3',
            'image4':'Изображение №4',
            'image5':'Изображение №5',
            'image6':'Изображение №6',
        }

        help_texts = {
            'image6': 'Следующие поля заполняются при их наличии и выводятся на экране "О Тренере"',
        }


class HelpTrainerForm(forms.ModelForm):
    group = forms.ModelMultipleChoiceField(label='Группы', queryset=Group.objects.filter(name__in=['trainers','dietologs','contentmanagers']))
    class Meta:
        model = Trainer
        fields = [
            'avatar',
            'phone',
            'content',
            'group',
        ]
        labels = {
            'avatar':'Аватар',
            'phone':'Телефон',
            'content':'Дополнительная информация',
        }


class UserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True, label='Имя')
    last_name = forms.CharField(required=True, label='Фамилия')

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2", 'first_name', 'last_name')

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not has_latin(username):
            raise forms.ValidationError("Должно содержать только латинские буквы.")
        return username

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


## USER UPDATE (TO-DO)

class UserChangeForm(UserChangeForm):
    first_name = forms.CharField(required=True, label='Имя')
    last_name = forms.CharField(required=True, label='Фамилия')

    class Meta:
        model = User
        fields = ("email", 'first_name', 'last_name')

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


#############################################################################################################################
## FOOD

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['product_input', 'weight']
        labels = {
            'product_input':'Продукт',
            'weight':'Количество',
        }

    def __init__(self, *args, **kwargs):
        super(FoodForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(

            )
        self.fields.get('product_input').widget.attrs['class'] = 'autocomplete'
        self.fields.get('weight').widget.attrs['min'] = 0
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs['placeholder'] = field.label


class FoodProgramForm(forms.ModelForm):
    class Meta:
        model = FoodProgram
        fields = ['name', 'content']
        labels = {
            'name':'Название программы питания (например, "для веганов")',
            'content':'Комментарии к питанию',
        }

class FoodProgramCloneForm(forms.ModelForm):
    class Meta:
        model = FoodProgram
        fields = ['client']
        labels = {
            'client':'Для какого клиента будет клонироваться программа питания?',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(FoodProgramCloneForm, self).__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(trainer=self.request.user.trainer)


class TimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ['settingstime']
        labels = {
            'settingstime':'Время приема пищи',
        }

    def __init__(self, *args, **kwargs):
        super(TimeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            )
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs['placeholder'] = field.label

#############################################################################################################################
## WORKOUT

class WsetForm(forms.ModelForm):
    class Meta:
        model = Wset
        fields = ['approach_number', 'rest_time', 'content']
        labels = {
        'approach_number':'Количество подходов',
        'rest_time':'Отдых после сета',
        'content':'Описание',
        }



class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['name', 'content', 'self_content', 'suggestions']
        labels = {
            'name':'Название тренировки (например, "Качаем спину")',
            'content':'Комментарии к тренировке',
            'self_content':'Только свой контент',
            'suggestions':'Включить помощник в подборе упражнений',
        }


class WorkoutCloneForm(ClientOwnerPermissionMixin, forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['client']
        labels = {
            'client':'Для какого клиента клонируется тренировка?',
        }
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(WorkoutCloneForm, self).__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(trainer=self.request.user.trainer)


class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['exercise','exercise_input', 'content', 'rest_time']
        labels = {
            'exercise_input':'Упражнение',
            'content':'Веса, комментарии к упражнению',
            'rest_time':'Отдых'
        }

    def __init__(self, *args, **kwargs):
        super(TrainingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(

            )
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = field_name
        self.fields.get('exercise_input').widget.attrs['class'] = 'autocomplete'

class ExerciseFilterForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = [
        'workout_occupation',
        'model_sex',
        'main_muscle',
        ]

        labels = {
            'workout_occupation':'Место',
            'model_sex':'Пол модели',
            'main_muscle':'Главные мышцы'
        }

    def __init__(self, *args, **kwargs):
        super(ExerciseFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(

            )
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = 'exercise-filter {0}'.format(field_name)
            field.widget.attrs['name'] = field



#############################################################################################################################
## PAY PROFILE FORMS

class PersonalWorkoutProfileForm(forms.ModelForm):
    class Meta:
        model = PersonalWorkoutProfile
        fields = [
            'country',
            'city',
            'disease',
            'purpose',
        ]

        labels = {
            'country':'Страна',
            'city':'Город',
            'disease':'Травмы и болезни (при наличии)',
            'purpose':'Цель тренировок',
        }

    def __init__(self, *args, **kwargs):
        client = kwargs.pop('client')
        super(PersonalWorkoutProfileForm, self).__init__(*args, **kwargs)


class PersonalNutrimentProfileForm(forms.ModelForm):
    class Meta:
        model = PersonalNutrimentProfile
        fields = [
            'daily_regime',
            'training_days',
            'allergy',
            'product_excepts_info',
            'product_accept',
        ]

        labels = {
            'daily_regime':'Ваш режим дня (время подъема, рабочее время и время сна)',
            'training_days':'Дни тренировок, их время и продолжительность',
            'allergy':'Наличие аллергии',
            'product_excepts_info':'Исключить продукты (подробнее)',
            'product_accept':'Какие продукты обязательно должны присутствовать в Вашем рационе',
        }

    def __init__(self, *args, **kwargs):
        client = kwargs.pop('client')
        super(PersonalNutrimentProfileForm, self).__init__(*args, **kwargs)


## COUNTERS
class PersonalWorkoutCounter(forms.ModelForm):
    class Meta:
        model = PersonalWorkoutProfile
        fields = [
            'workout_counter',
        ]

        labels = {
            'workout_counter':'Добавить тренировок',
        }


class PersonalNutrimentCounter(forms.ModelForm):
    class Meta:
        model = PersonalNutrimentProfile
        fields = [
            'nutriment_counter',
        ]

        labels = {
            'nutriment_counter':'Добавить программ питания',
        }









