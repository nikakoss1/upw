# -*- coding: utf-8 -*-
from django.db import models
from preferences.models import Preferences

PROGRAM_TYPE_CHOICES = [
        ("WP","Индивидуальные тренировки от тренера"),
        ("FP","Индивидуальное питание от тренера"),
        ("WG","Тренировки по категориям"),
        ("WC","Тренировки по упражнениям"),
        ("FG","Питание"),
        ("MT","Марафон (тренировки + питание)"),
        ("EX","Эксклюзивные программы (тренировки + питание)"),
    ]

SEX = [
        ("M","Муж"),
        ("F","Жен")
    ]

LEVELS = [
        ("N","Сидячий образ жизни"),
        ("M","Умеренная активность (нагрузки 1-3 раза в неделю)"),
        ("A","Средняя активность (нагрузки 3-5 раз в неделю)"),
        ("P","Активные люди (нагрузки 6-7 раз в неделю)"),
    ]

KA = {
    'N':'1.2',
    'M':'1.375',
    'A':'1.55',
    'P':'1.725',
}

PRODUCT_MEAL_CHOICES = [
        ("P","Продукт"),
        ("M","Готовое блюдо")
    ]

BLOGER_STATUS = [
        ("default","Нет ответа"),
        ("primary","Думает"),
        ("success","Подключен"),
        ("danger","Отказ"),
    ]

PROGRAM_LOCATION = [
        ("fitness","В зале"),
        ("workout","На улице"),
        ("home","Дома"),
    ]

PROGRAM_LEVEL = [
        ("start","Начальный"),
        ("middle","Средний"),
        ("pro","Продвинутый"),
    ]

WELCOME_MESSAGE = "Мы активировали для Вас полный доступ к каталогу тренировок и питания на 7 дней, не забудьте подписаться на наш канал в инстаграмме @nasporte.online. Скажите, Вы планируете заниматься самостоятельно или с тренером?"

class AppSettings(Preferences):
    brand = models.CharField('Бренд', max_length=255, blank=True, null=True)
    mobile_app_token = models.CharField(max_length=30, blank=True, null=True )
    logo1 = models.ImageField()
    logo2 = models.ImageField()
    coming_soon = models.BooleanField(default=False)
    maintenance = models.BooleanField(default=False)
    personal_demo_testing = models.BooleanField('Режим тестирования персонального раздела', default=False)
    general_workout_exercise_rest_time = models.PositiveIntegerField(default=60)
    memberzone_price = models.IntegerField('Стоимость доступа к каталогу в месяц', default=500)
    personal_workout_price = models.IntegerField('Стоимость 1 персональной тренировки', default=125)
    personal_pp_price = models.IntegerField('Стоимость 1 персональной ПП', default=1000)
    various_food_generation_mode = models.BooleanField('Разнообразный режим генерации питания (много блюд)', default=True)
    fatten_percent = models.PositiveIntegerField(default=20)
    loseweight_persent = models.PositiveIntegerField(default=20)
    oferta = models.TextField(blank=True, null=True)
    rekv = models.TextField(blank=True, null=True)
    new_message_send_email = models.BooleanField(default=True)

    def __str__(self):
        return 'Settings_object: %s' % self.id

class CompetitionStatus(models.Model):
    status = models.CharField('Статус', max_length=255, blank=True, null=True)

    def __str__(self):
        return '%s' % self.status

class Unit(models.Model):
    name = models.CharField('Единицы измерения в продуктах', max_length=30, blank=False, null=False)

    def __str__(self):
        return '%s' % self.name

class Subscriber(models.Model):
    mail = models.EmailField('Email', max_length=50, blank=False, null=False)

    def __str__(self):
        return '%s' % self.mail

class SettingsDay(models.Model):
    name = models.CharField('День недели', max_length=100, blank=False, null=False)

    def __str__(self):
        return '%s' % self.name


class SettingsTime(models.Model):
    name = models.TimeField('Время приема пищи', blank=False, null=False)

    def __str__(self):
        return '%s' % self.name


class SettingsRestTime(models.Model):
    value = models.PositiveIntegerField('Секунды', blank=False, null=True)
    name = models.CharField('Отдых', max_length=200, blank=False, null=True)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        ordering = ['value']

class ExerciseCommentName(models.Model):
    name = models.CharField('Название', max_length=200, blank=False, null=False)
    name_id = models.PositiveIntegerField(default=0)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.name

class WorkoutCommentName(models.Model):
    name = models.CharField('Название', max_length=200, blank=False, null=False)
    name_id = models.PositiveIntegerField(default=0)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.name


class MainMuscle(models.Model):
    content = models.CharField(max_length=120, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.content

    class Meta:
        ordering = ['content']


class OtherMuscle(models.Model):
    name = models.CharField(max_length=120, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        ordering = ['name']


class ExerciseType(models.Model):
    content = models.CharField(max_length=120, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.content

    class Meta:
        ordering = ['content']


class Biomech(models.Model):
    content = models.CharField(max_length=120, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.content

    class Meta:
        ordering = ['content']


class Vektor(models.Model):
    content = models.CharField(max_length=120, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.content

    class Meta:
        ordering = ['content']


class Equipment(models.Model):
    content = models.CharField(max_length=120, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.content

    class Meta:
        ordering = ['content']


class DifficultyLevel(models.Model):
    content = models.CharField(max_length=120, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.content

    class Meta:
        ordering = ['content']


class RecipeType(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class RecipeFoodType(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class RecipeAppointment(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class RecipeMode(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class RecipeCooktime(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class RecipeCookmethod(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class CatalogOrderTime(models.Model):
    days = models.IntegerField(default=30)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.days


class PersonalWorkoutBuyPackage(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)
    number = models.IntegerField(default=12)
    price = models.FloatField(default=125)

    def __str__(self):
        return '%s' % self.name


class PersonalPPBuyPackage(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)
    number = models.IntegerField(default=1)
    price = models.FloatField(default=1000)

    def __str__(self):
        return '%s' % self.name


class WorkoutOccupation(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.name


class ModelSex(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.name


class WelcomeMessage(models.Model):
    content = models.TextField(max_length=255, null=True, blank=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.content





