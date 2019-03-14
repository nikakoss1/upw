# -*- coding: utf-8 -*-
from .models import (
    Program,
    Feature,
    TrainingTemplate,
    WorkoutTemplate,
    WsetTemplate,
    Training,
    FoodProgramTemplate,
    FoodTemplate,
    TimeTemplate,
    )
from appsettings.models import (
    PROGRAM_TYPE_CHOICES,
    )
from preferences import preferences
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, ButtonHolder, Submit, Field, HTML
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import formset_factory
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from accounts.workout_models import (
    Training,
    Workout,
    Wset,
    )

#############################################################################################################################
## WORKOUT PROGRAMS

class ProgramCreateForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = [
            'img',
            'name',
            'short_desc',
            'desc',
            'program_type',
            'rating',
        ]
        labels = {
            'img':'Картинка',
            'name':'Название программы',
            'program_type':'Тип программы',
            'rating':'Рейтинг',
            'desc':'Описание',
        }
        widgets = {
            'desc': SummernoteInplaceWidget(),
            }

    def __init__(self, *args, **kwargs):
        super(ProgramCreateForm, self).__init__(*args, **kwargs)

        CHOICES = []
        exclude_lst = []
        for program_type in ['WP', 'FP']:
            if Program.objects.filter(program_type=program_type).first():
                exclude_lst.append(program_type)

        for item in PROGRAM_TYPE_CHOICES:
            if not item[0] in exclude_lst:
                CHOICES.append(item)
        self.fields['program_type'] = forms.ChoiceField(label='Тип программы', choices = set(CHOICES))


class ProgramUpdateForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = [
            'img',
            'program_location',
            'program_level',
            'name',
            'short_desc',
            'desc',
            'content_owner',
            'category',
            'rating',
            'demo',
            'to_all',
            'daily',
            'chargeable',
            'is_active',

        ]
        labels = {
            'img':'Картинка',
            'program_location':'Место',
            'program_level':'Уровень',
            'category':'Категория',
            'is_active':'Активный',
            'content_owner':'Владелец контента',
            'demo':'Демо',
            'name':'Название программы',
            'rating':'Рейтинг',
            'desc':'Описание',
            'to_all':'Для всех (муж + жен)',
            'daily':'Ежедневные тренировки',
            'chargeable':'Платная',
        }
        widgets = {
            'desc': SummernoteInplaceWidget(),
            }

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop("pk")
        super(ProgramUpdateForm, self).__init__(*args, **kwargs)
        program_obj = Program.objects.get(id=pk)

        if not program_obj.program_type in ['WG', 'WC','MT', 'EX']:
            del self.fields['to_all']

        if not program_obj.program_type == 'WG':
            del self.fields['daily']

        if program_obj.program_type in ['WP','FP']:
            del self.fields['demo']

        if program_obj.program_type in ['FG',]:
            del self.fields['content_owner']


class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = [
            'name',
        ]
        labels = {
            'name':'Преимущества',
        }

    def __init__(self, *args, **kwargs):
        super(FeatureForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            )

        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs['placeholder'] = field.label


#############################################################################################################################
## WORKOUT TEMPLATES FORMS

class TemplateTypeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(TemplateTypeForm, self).__init__(*args, **kwargs)
        self.fields['template_type'] = forms.ChoiceField(label='Тип', required=True, choices = PROGRAM_TYPE_CHOICES1)


class WorkoutTemplateForm(forms.ModelForm):
    class Meta:
        model = WorkoutTemplate
        fields = [
            'rest',
            'name',
            'sex',
            'training_level',
        ]
        labels = {
            'name':'Название шаблона тренировки',
            'sex':'Пол',
            'training_level':'Уровень физ активности',
            'rest':'День отдыха',
        }


class WsetTemplateForm(forms.ModelForm):
    class Meta:
        model = WsetTemplate
        fields = [
            'approach_number',
            'rest_time',
        ]
        labels = {
            'approach_number':'Количество подходов в данном сете',
            'rest_time':'Отдых после данного сета',
        }


class TrainingTemplateForm(forms.ModelForm):
    class Meta:
        model = TrainingTemplate
        fields = [
            'workout_occupation',
            'main_muscle',
            'other_muscle',
            'exercise_type',
            'biomech',
            'vektor',
            'equipment',
            'difficulty_level',
            'repetition',
        ]

        labels = {
            'workout_occupation':'Место',
            'main_muscle':'Основные мышцы',
            'other_muscle':'Дополнительные мышцы',
            'exercise_type':'Тип',
            'biomech':'Биомеханика',
            'vektor':'Вектор',
            'equipment':'Оборудование',
            'difficulty_level':'Сложность',
            'repetition':'Повторения',
        }

    def __init__(self, *args, **kwargs):
        super(TrainingTemplateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            )

        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs['title'] = field.label
        self.fields['workout_occupation'].widget.attrs['class'] = 'workout_occupation'
        self.fields['main_muscle'].widget.attrs['class'] = 'main_muscle'
        self.fields['other_muscle'].widget.attrs['class'] = 'other_muscle'
        self.fields['exercise_type'].widget.attrs['class'] = 'exercise_type'
        self.fields['biomech'].widget.attrs['class'] = 'biomech'
        self.fields['vektor'].widget.attrs['class'] = 'vektor'
        self.fields['equipment'].widget.attrs['class'] = 'equipment'
        self.fields['difficulty_level'].widget.attrs['class'] = 'difficulty_level'


class CustomTrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['exercise_input', 'content', 'rest_time']
        labels = {
            'exercise_input':'Упражнение',
            'content':'Веса, комментарии к упражнению',
            'rest_time':'Отдых'
        }

    def __init__(self, *args, **kwargs):
        super(CustomTrainingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(

            )
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = field_name
        self.fields.get('exercise_input').widget.attrs['class'] = 'autocomplete'


#############################################################################################################################
## CUSTOM WORKOUT FORMS

class CustomWorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = [
            'rest',
            'name',
            'sex',
            'training_level',
        ]
        labels = {
            'name':'Название тренировки',
            'sex':'Пол',
            'training_level':'Уровень физ активности',
            'rest':'День отдыха',
        }


class WsetForm(forms.ModelForm):
    class Meta:
        model = Wset
        fields = [
            'approach_number',
            'rest_time',
            'content',
        ]
        labels = {
            'approach_number':'Количество подходов в данном сете',
            'rest_time':'Отдых после данного сета',
            'content':'Описание'
        }


class CustomTrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['exercise','exercise_input', 'content', 'rest_time']
        labels = {
            'exercise_input':'Упражнение',
            'content':'Веса, комментарии к упражнению',
            'rest_time':'Отдых'
        }

    def __init__(self, *args, **kwargs):
        super(CustomTrainingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(

            )
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['class'] = field_name
        self.fields.get('exercise_input').widget.attrs['class'] = 'autocomplete'


#############################################################################################################################
## FOODPROGRAM TEMPLATE FORM

class FoodProgramTemplateForm(forms.ModelForm):
    class Meta:
        model = FoodProgramTemplate
        fields = [
            'name',
            'kf',
        ]
        labels = {
            'name':'Название шаблона питания',
            'kf':'Коэффициент изменения дневного калоража (например, 0.8 или 1.2)',
        }


class FoodTemplateForm(forms.ModelForm):
    class Meta:
        model = FoodTemplate
        fields = ['product_input', 'weight']
        labels = {
            'product_input':'Продукт',
            'weight':'Количество',
        }

    def __init__(self, *args, **kwargs):
        super(FoodTemplateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(

            )
        self.fields.get('product_input').widget.attrs['class'] = 'autocomplete'
        self.fields.get('weight').widget.attrs['min'] = 0
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs['placeholder'] = field.label


class TimeTemplateForm(forms.ModelForm):
    class Meta:
        model = TimeTemplate
        fields = ['settingstime']
        labels = {
            'settingstime':'Время приема пищи',
        }

    def __init__(self, *args, **kwargs):
        super(TimeTemplateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            )
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs['placeholder'] = field.label

