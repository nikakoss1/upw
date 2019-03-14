# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import (
    Muscle,
    Exercise,
    FitnessClub,
    FitnessClubImage,
    Product,
    Competition,
    Unit,
    Kbzu1Portion,
    Kbzu100g,
    )
from django import forms
from django.utils import timezone
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

def file_size(value): # add this to some file where you can import it from
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Файл слишком большой, размер не должен превышать 2МБ.')


class MuscleForm(forms.ModelForm):
    class Meta:
        model = Muscle
        fields = ['name',]

class FitnessClubForm(forms.ModelForm):
    class Meta:
        model = FitnessClub
        fields = ['name', 'content', 'video_url']
        labels = {
            'name':'Название фитнес-клуба',
            'content':'Комментарий',
            'video_url':'Видео с тренажерами',
        }

class FitnessClubImageForm(forms.ModelForm):
    class Meta:
        model = FitnessClubImage
        fields = ['image',]
        labels = {
            'image':'Изображения тренажеров',
        }


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = [
            'approved',
            'name',
            'workout_occupation',
            'model_sex',
            'main_muscle',
            'other_muscle',
            'exercise_type',
            'biomech',
            'vektor',
            'equipment',
            'difficulty_level',
            'content',
            'short_video',
            'video',
        ]
        labels = {
            'approved':'Подтверждено',
            'name':'Название упражнения',
            'workout_occupation':'Место',
            'model_sex':'Пол',
            'main_muscle':'Целевые мышцы',
            'other_muscle':'Дополнительные мышцы',
            'exercise_type':'Тип упражнения',
            'biomech':'Биомеханика',
            'vektor':'Вектор силы',
            'equipment':'Оборудование',
            'difficulty_level':'Сложность',
            'content':'Описание',
            'short_video':'УРЛ короткого видео',
            'video':'УРЛ подробного видео',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ExerciseForm, self).__init__(*args, **kwargs)
        if not self.request.user.trainer.is_boss == True:
            del self.fields['approved']


class Kbzu1PortionForm(forms.ModelForm):
    class Meta:
        model = Kbzu1Portion
        fields = ['weight', 'protein', 'fat', 'carbohydrate', 'kkal']
        labels = {
            'weight':'Расчетный вес',
            'protein':'Белки',
            'fat':'Жиры',
            'carbohydrate':'Углеводы',
            'kkal':'ККАЛ',
        }


class Kbzu100gForm(forms.ModelForm):
    class Meta:
        model = Kbzu100g
        fields = ['weight', 'protein', 'fat', 'carbohydrate', 'kkal']
        labels = {
            'weight':'Расчетный вес',
            'protein':'Белки',
            'fat':'Жиры',
            'carbohydrate':'Углеводы',
            'kkal':'ККАЛ',
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name',]
        labels = {
            'name':'Название продукта',
        }


class CompetitionForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.SelectDateWidget(),initial=timezone.now, label='Дата начала конкурса')
    finish_date = forms.DateField(widget=forms.SelectDateWidget(),initial=timezone.now, label='Дата окончания конкурса')
    class Meta:
        model = Competition
        fields = ['name','content','image', 'video', 'start_date','finish_date', 'status']
        widgets = {
                    'content': SummernoteInplaceWidget(),
                }
        labels = {
            'name':'Название конкурса',
            'image':'Картинка конкурса',
            'video':'Видео',
            'content':'Описание конкурса',
            'status':'Статус',
            'start_date':'Дата начала конкурса',
            'finish_date':'Дата окончания конкурса',
        }



