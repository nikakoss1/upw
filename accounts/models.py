# -*- coding: utf-8 -*-
from activities.models import Activity
from appsettings.models import (
    SettingsDay,
    SettingsTime,
    SettingsRestTime,
    WorkoutCommentName,
    SEX,
    LEVELS,
    )
from .utils import add_activity
from .workout_models import *
from appsettings.utils import *
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mass_mail
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import signals
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import date as _date
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from memberzone.models import Order
from options.models import Competition, FitnessClub, Product, Exercise
from preferences import preferences
from subscriptions.models import Program
import math, datetime
from datetime import datetime, timedelta
from celery import shared_task
from sportapps.celery import app
from django.core import mail
from chat.onesygnal import send_push_message
from appsettings.models import WELCOME_MESSAGE
from celery.task.control import inspect




now = datetime.now().date()

#############################################################################################################################
## HELP FUNCS

def account_uploads(instance, filename, *args, **kwargs):
    return 'accounts/users/%s' % filename


def progress_uploads(instance, filename):
    return "accounts/progress/%s" % filename

def send_notify_email(text, mail):
    EmailMessage('Новое сообщение', text, to=[mail]).send()

#############################################################################################################################
## MOBILE USER


def check_age(age):
    if age > 100 or age < 18:
        return 18
    return age


class LeadUser(models.Model):
    uuid = models.SlugField(unique=True)
    chatid = models.CharField(max_length=255, null=True, blank=False)
    is_banned = models.BooleanField(default=False)
    age = models.FloatField(default=0)
    high = models.FloatField(default=0)
    weight = models.FloatField(default=0)
    wish_weight = models.FloatField(default=0)
    sex = models.CharField('Пол', max_length=1, choices=SEX)
    training_level = models.CharField('Уровень физ подготовки', max_length=1, choices=LEVELS)
    promo = models.CharField('Промокод', max_length=25, null=True, blank=False)

    # CHAT
    new_messages_from_trainer = models.BooleanField(default=True)
    new_messages_from_client = models.BooleanField(default=False)

    ## OTHER
    bok = models.FloatField(default=2500) # БАЗОВЫЙ КАЛОРАЖ
    dk = models.FloatField(default=2300) # СУТОЧНЫЙ КАЛОРАЖ
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)


    class Meta:
        ordering = ['-new_messages_from_client']

    def __str__(self):
        return "user: %s, %s" % (self.id, self.is_banned)


    def get_absolute_url(self):
        return reverse("accounts:leaduser_detail", kwargs={"pk":self.pk, 'chatid':self.chatid})

    def ban_user(self):
        self.is_banned = True
        self.save()

    def remove_ban_user(self):
        self.is_banned = False
        self.save()

    def clean(self):
        if self.age < 18 or self.age > 100:
            raise ValidationError({'age':'Age is not correct'})
        if self.high < 140 or self.high > 220:
            raise ValidationError({'high':'High is not correct'})
        if self.weight < 40 or self.weight > 150:
            raise ValidationError({'weight':'Weight is not correct'})
        if self.wish_weight < 40 or self.wish_weight > 150:
            raise ValidationError({'wish_weight':'Wish weight is not correct'})


    def save(self, *args, **kwargs):
        with transaction.atomic():
            age = self.age
            high = self.high
            weight = self.weight
            wish_weight = self.wish_weight
            sex = self.sex
            training_level = self.training_level
            self.bok, self.dk = get_bok_ck(weight, age, high, training_level, sex)
            self.chatid = get_random_string(length=12)
            super(LeadUser, self).save(*args, **kwargs)


#############################################################################################################################
## TRAINER CRUD

class Trainer(models.Model):
    main_trainer = models.ForeignKey('self', null=True, blank=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=account_uploads, default='accounts/noavatar.png')
    is_boss = models.BooleanField(default=False)
    city = models.CharField('Город', max_length=50)
    content = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=50)
    skype = models.CharField(max_length=100, null=True, blank=True)
    whatsapp = models.CharField(max_length=50, null=True, blank=True)
    mail = models.EmailField(max_length=100, null=True, blank=True)
    vk = models.URLField(max_length=300, null=True, blank=True)
    ok = models.URLField(max_length=300, null=True, blank=True)
    instagram = models.URLField(max_length=300, null=True, blank=True)
    fb = models.URLField(max_length=300, null=True, blank=True)
    yt = models.URLField(max_length=300, null=True, blank=True)
    promo_video = models.URLField(max_length=300, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)
    # IF IS BOSS
    image1 = models.ImageField(upload_to=account_uploads, blank=True, null=True)
    image2 = models.ImageField(upload_to=account_uploads, blank=True, null=True)
    image3 = models.ImageField(upload_to=account_uploads, blank=True, null=True)
    image4 = models.ImageField(upload_to=account_uploads, blank=True, null=True)
    image5 = models.ImageField(upload_to=account_uploads, blank=True, null=True)
    image6 = models.ImageField(upload_to=account_uploads, blank=True, null=True)

    def __str__(self):
        return "%s" % self.user.get_full_name()

    def get_delete_url(self):
        return reverse("accounts:trainer_delete", kwargs = {"pk":self.pk})

    def get_detail_url(self):
        return reverse("accounts:trainer_detail", kwargs={"pk":self.pk})

    def get_absolute_url(self):
        return reverse("accounts:trainer_detail", kwargs={"pk":self.pk})

    def get_update_url(self):
        return reverse("accounts:trainer_update", kwargs={"pk":self.pk})

    def get_help_trainers(self):
        return self.trainer_set.all().count()

    def trainer_enable(self):
        self.user.is_active = True
        self.user.save()

    def trainer_disable(self):
        self.user.is_active = False
        self.user.save()

    def delete(self):
        if self.user:
            self.user.delete()
        super(Trainer, self).delete()

    # def get_promocode(self):
    #     partner = Partner.objects.get(trainer=self)
    #     promocode = partner.promocode
    #     return promocode


#############################################################################################################################
## CLIENT CRUD

class Client(models.Model):
    ## REGISTRATION
    leaduser = models.ForeignKey(LeadUser, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    patronymic = models.CharField(max_length=120, null=True, blank=True)
    phone = models.CharField('Телефон', max_length=25, null=True, blank=True)
    age = models.FloatField('Возраст', default=18)
    high = models.FloatField('Рост', default=0)
    weight = models.FloatField('Текущий вес', default=0)
    wish_weight = models.FloatField('Желаемый вес')
    sex = models.CharField('Пол', max_length=1, choices=SEX)
    training_level = models.CharField('Уровень физ подготовки', max_length=1, choices=LEVELS)
    identifier = models.CharField(max_length=255, null=True, blank=True)

    # CHAT
    new_messages_from_trainer = models.BooleanField(default=False)
    new_messages_from_client = models.BooleanField(default=False)

    ## PROFILES
    workout_profile_completed = models.BooleanField('Профиль для персональных тренировок заполнен', default=False)
    nutriment_profile_completed = models.BooleanField('Профиль для персонального питания заполнен', default=False)

    ## OTHER
    bok = models.FloatField(default=2500) # БАЗОВЫЙ КАЛОРАЖ
    dk = models.FloatField(default=2300) # ЦЕЛЕВОЙ КАЛОРАЖ
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True)
    programs = models.ManyToManyField(Program, blank=True)
    uuid = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    avatar = models.ImageField(upload_to=account_uploads, default='accounts/noavatar.png')
    is_member = models.BooleanField(default=True)
    is_banned = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    ref_promo = models.CharField(max_length=70, null=True, blank=True)
    oferta = models.BooleanField('С условиями оферты согласен(-а)', default=False)
    konf = models.BooleanField('С условиями политики конфиденциальности согласен(-а)', default=False)
    regenerate_food = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['-created']


    def __str__(self):
        return "%s" % self.user.get_full_name()

    def get_delete_url(self):
        return reverse("accounts:client_delete", kwargs = {"slug":self.slug})

    def get_detail_url(self):
        return reverse("accounts:client_detail", kwargs={"slug":self.slug})

    def get_absolute_url(self):
        return reverse("accounts:client_detail", kwargs={"slug":self.slug})

    def get_notupdate_url(self):
        return reverse("accounts:client_note_update", kwargs={"slug":self.slug})

    def change_trainer(self):
        return reverse("accounts:client_change_trainer", kwargs={"slug":self.slug})

    def get_user_groups(user):
        return Group.objects.filter(user=user)

    def get_main_trainer(self):
        if not self.trainer:
            return None
        trainer_user = self.trainer.user
        if has_group(trainer_user, 'brandowners'):
            return self.trainer
        elif has_group(trainer_user, 'main_trainers'):
            return self.trainer
        elif has_group(trainer_user, 'trainers'):
            return self.trainer.main_trainer

    def get_trainer(self):
        return self.trainer

    def get_counters_url(self):
        return reverse("accounts:counters_update", kwargs={"slug":self.slug})

    def member(self):
        client_last_order = self.order_set.filter(catalog=True, payed=True).last()
        end_date = client_last_order.created + timedelta(days=client_last_order.catalog_order_time)
        if end_date > now:
            return (True, end_date)
        return (False,)

    def client_enable(self):
        self.user.is_active = True
        self.user.save()

    def client_disable(self):
        self.user.is_active = False
        self.user.save()

    # def is_first_buyer(self):
    #     if self.order_set.all().exists():
    #         return False
    #     return True

    def personal_workout_profile_is_active(self):
        if self.personalworkoutprofile.workout_counter > 0:
            return True
        else:
            False

    def personal_nutriment_profile_is_active(self):
        if self.personalnutrimentprofile.nutriment_counter > 0:
            return True
        else:
            False

    def sex_value(self):
        for choice in SEX:
            if choice[0] == 'M':
                return choice[1]
            elif choice[0] == 'F':
                return choice[1]

    def level_value(self):
            for choice in LEVELS:
                if choice[0] == 'N':
                    return choice[1]
                elif choice[0] == 'M':
                    return choice[1]
                elif choice[0] == 'A':
                    return choice[1]
                elif choice[0] == 'P':
                    return choice[1]

    def clean(self, *args, **kwargs):
        if self.age < 18 or self.age > 100:
            raise ValidationError({'age':'Age is not correct'})
        if self.high < 140 or self.high > 220:
            raise ValidationError({'high':'High is not correct'})
        if self.weight < 40 or self.weight > 150:
            raise ValidationError({'weight':'Weight is not correct'})
        if self.wish_weight < 40 or self.wish_weight > 150:
            raise ValidationError({'wish_weight':'Wish weight is not correct'})

    def has_changed_or_init(self, *args, **kwargs):
        try:
            orig = Client.objects.get(id=self.id)
        except:
            return False
        if orig.age != self.age:
            return True
        if orig.high != self.high:
            return True
        if orig.weight != self.weight:
            return True
        if orig.wish_weight != self.wish_weight:
            return True
        if orig.sex != self.sex:
            return True
        if orig.training_level != self.training_level:
            return True
        return False

    def save(self, *args, **kwargs):
        try:
            if self.has_changed_or_init(self, *args, **kwargs):
                foodprogram_generator(self, **kwargs)
            age = self.age
            high = self.high
            weight = self.weight
            wish_weight = self.wish_weight
            sex = self.sex
            training_level = self.training_level
            self.bok, self.dk = get_bok_ck(weight, age, high, training_level, sex)
            self.chatid = get_random_string(length=12)
            super(Client, self).save(*args, **kwargs)
        except Exception as e:
            print(e)

# def send_mail(title, from_mail, to_mail):
#     title = 'Новое сообщение от {0}'.format(client.user.get_full_name())
#     from_mail = 'nasporte.online@gmail.com'
#     to_mail = client.trainer.user.email
#     emails = (
#         (
#             title,
#             message,
#             from_mail,
#             [to_mail]
#             ),
#         )
#     results = mail.send_mass_mail(emails)
#     return results[0].id


@receiver(post_save, sender=Client)
def client_activity(sender, instance, **kwargs):
    if kwargs['created']:
        return add_activity(client=instance, new_client=True, content='Зарегистрирован новый член команды.')
    return


#############################################################################################################################
## CLIENT NOTES

class Note(models.Model):
    client = models.OneToOneField(Client, blank=False)
    content = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.client

@receiver(post_save, sender=Client)
def create_note(sender, instance, **kwargs):
    if kwargs['created']:
        return Note.objects.create(client=instance)
    return


#############################################################################################################################
## Progress

class Progress(models.Model):
    is_completed = models.BooleanField(default=False)
    client = models.ForeignKey(Client)
    image1 = models.ImageField('Спереди', upload_to=progress_uploads)
    image2 = models.ImageField('Сбоку', upload_to=progress_uploads)
    image3 = models.ImageField('Сзади', upload_to=progress_uploads)
    current_weight = models.FloatField('Текущий вес', default=0)
    chest = models.FloatField('Объем груди', default=0)
    waistline = models.FloatField('Талия', default=0)
    hip = models.FloatField('Бедра', default=0)
    leg = models.FloatField('Объем ноги', default=0)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id

    class Meta:
        ordering = ['-created']

    def save(self, *args, **kwargs):
        super(Progress, self).save(*args, **kwargs)

# @receiver(post_save, sender=Progress)
# def progress_activity(sender, instance, **kwargs):
#     if  kwargs['created']:
#         return add_activity(client=instance.client, progress=instance)
#     return


#############################################################################################################################
#  PROFILES

class PersonalWorkoutProfile(models.Model):
    workout_counter = models.PositiveIntegerField(default=0)
    client = models.OneToOneField(Client)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    disease = models.TextField('Травмы и болезни (при наличии)', null=True, blank=True)
    purpose = models.TextField('Цель тренировок', null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.client.user.username

    def count_limit(self):
        return 'Активных тренировок: {0}'.format(self.workout_counter)


## PERSONAL NUTRIMENT PROFILE
class PersonalNutrimentProfile(models.Model):
    client = models.OneToOneField(Client)
    nutriment_counter = models.PositiveIntegerField(default=0)
    daily_regime = models.TextField('Режим дня', null=True, blank=True)
    training_days = models.TextField('Тренировочные дни', null=True, blank=True)
    allergy = models.TextField('Наличие аллергии', null=True, blank=True)
    product_excepts_info = models.TextField('Какие продукты необходимо исключить?', null=True, blank=True)
    product_accept = models.TextField('Какие продукты обязательны', null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.client.user.username

    def count_limit(self):
        return 'Программ питания для составления: {0}'.format(self.nutriment_counter)


@receiver(post_save, sender=PersonalWorkoutProfile)
def workout_profile_completed_post_save(sender, instance, **kwargs):
    if not kwargs['created']:
        client_obj = instance.client
        client_obj.workout_profile_completed = True
        client_obj.save()
    return

@receiver(post_save, sender=PersonalNutrimentProfile)
def nutiment_profile_completed_post_save(sender, instance, **kwargs):
    if not kwargs['created']:
        client_obj = instance.client
        client_obj.nutriment_profile_completed = True
        client_obj.save()
    return



#############################################################################################################################
## CHAT TAB

class Message(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    leaduser = models.ForeignKey(LeadUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='leadmessages')
    handle = models.TextField()
    userhandle = models.CharField(max_length=120, blank=True, null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    new = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s | %s" % (self.handle, self.timestamp)

    def as_dict(self):
        return {'handle': self.handle, 'message': self.message, 'timestamp': _date(self.timestamp, "d b, D"), 'userhandle':self.userhandle}

    @property
    def websocket_group(self):
        """
        Returns the Channels Group that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return Group("client-%s" % self.id)

    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)
        if preferences.AppSettings.new_message_send_email:
            if self.userhandle == 'client':
                text = self.message
                mail = self.client.trainer.user.email
                send_notify_email(str(text), mail)

#############################################################################################################################
## FOOD TAB

class FoodProgram(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True)
    program = models.ForeignKey(Program, null=True, blank=True)
    leaduser = models.ForeignKey(LeadUser, null=True, blank=True)
    number = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=100, null=True, blank=False)
    content = models.TextField(max_length=255, null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['-created']

    def get_member_foodprogram_detail_url(self):
        return reverse("members:member_foodprogram_detail", kwargs={"pk":self.pk})

    def __str__(self):
        return "%s:%s" % (self.name if self.name is not None else self.program, self.created)

    def get_content(self):
        return self.content if self.content != None else ''


@receiver(post_save, sender=FoodProgram)
def counter_decrease(sender, instance, **kwargs):
    if instance.program.program_type == 'FG':
        return
    if instance.client:
        if kwargs['created']:
            personal_foodprogram_profile_obj = instance.client.personalnutrimentprofile
            if personal_foodprogram_profile_obj.nutriment_counter > 0:
                personal_foodprogram_profile_obj.nutriment_counter = personal_foodprogram_profile_obj.nutriment_counter-1
                personal_foodprogram_profile_obj.save()
    return

@receiver(post_save, sender=FoodProgram)
def foodprogram_activity(sender, instance, **kwargs):
    if  kwargs['created']:
        if not Activity.objects.filter(foodprogram=instance).first():
            return add_activity(client=instance.client, foodprogram=instance, content='Добавлена новая программа питания "{}"'.format(instance.name))
    return


class Day(models.Model):
    foodprogram = models.ForeignKey(FoodProgram, null=True, blank=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    sorting = models.IntegerField(null=True, blank=False)
    day_kbzu = models.FloatField(null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        ordering = ['sorting']

    def get_member_day_detail(self):
        return reverse("members:member_day_detail", kwargs={"pk":self.pk})

    def get_day_kbzu(self):
        kkal = 0
        protein = 0
        fat = 0
        carbohydrate = 0
        for time in self.time_set.all():
            kkal += time.kkal
            protein += time.protein
            fat += time.fat
            carbohydrate += time.carbohydrate
        return kkal, protein, fat, carbohydrate

    def get_day_recipes(self):
        lst = []
        for time in self.time_set.all():
            for food in time.food_set.all():
                name = food.product.name
                recipe = food.product.recipe
                ingridients = recipe.ingridients
                instructions = recipe.instructions
                lst.append((name, ingridients, instructions))
        return lst


class Time(models.Model):
    number = models.PositiveIntegerField(default=0)
    settingstime = models.ForeignKey(SettingsTime, null=True, blank=False)
    day = models.ForeignKey(Day, null=True, blank=False)
    weight = models.FloatField(default=0, blank=False, null=True)
    kkal = models.FloatField(default=0, blank=False, null=True)
    protein = models.FloatField(default=0, blank=False, null=True)
    fat = models.FloatField(default=0, blank=False, null=True)
    carbohydrate = models.FloatField(default=0, blank=False, null=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.settingstime

    class Meta:
        ordering = ['number']


class Food(models.Model):
    foodprogram = models.ForeignKey(FoodProgram, null=True, blank=False)
    day = models.ForeignKey(Day, null=True, blank=True)
    time = models.ForeignKey(Time, null=True, blank=False)
    product = models.ForeignKey(Product, null=True, blank=False)
    product_input = models.CharField(max_length=255, null=True, blank=False)
    weight = models.FloatField(default=0, blank=False, null=True)
    kkal = models.FloatField(default=0, blank=False, null=True)
    protein = models.FloatField(default=0, blank=False, null=True)
    fat = models.FloatField(default=0, blank=False, null=True)
    carbohydrate = models.FloatField(default=0, blank=False, null=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        # return "%s" % self.id
        # return "%s / %s / %s / %s ккал / %s г" % (self.day, self.time, self.product, self.kkal, self.weight)
        return "%s / %s / %s / %s ккал / %s г / %s пор" % (self.day, self.time, self.product, self.kkal, self.weight, self.weight/self.product.kbzu_1portion.weight)

    def get_delete_url(self):
        return reverse("accounts:food_delete")

    def get_portion_numbers(self):
        if self.product.kbzu_1portion:
            portion = self.weight/self.product.kbzu_1portion.weight
        elif self.product.kbzu_100g:
            portion = self.weight/self.product.kbzu_100g.weight
        return portion


@receiver(pre_save, sender=Food)
def time_kbzu_post_save(sender, instance, **kwargs):
    time_obj = instance.time
    time_obj.weight += instance.weight
    time_obj.kkal += instance.kkal
    time_obj.protein += instance.protein
    time_obj.fat += instance.fat
    time_obj.carbohydrate += instance.carbohydrate
    time_obj.save()
    return


#########################################################################################################################
####### FOODPROGRAM GENERATOR
# LOSEWEIGHT_KF = 0.7
# FATTEN = 1.2

# CK_PROGRAM_NAME = (
#     (LOSEWEIGHT_KF,'Программа питания для похудения'),
#     (1,'Здоровое питание'),
#     (FATTEN,'Программа питания для набора массы'),
#     )

# def is_leaduser(instance):
#     return instance.__class__.__name__ == 'LeadUser'

# def get_foodprogram(program_obj, instance):
#     if is_leaduser(instance):
#         foodprogram_obj, created = FoodProgram.objects.get_or_create(program=program_obj, leaduser=instance)
#     else:
#         foodprogram_obj, created = FoodProgram.objects.get_or_create(program=program_obj, client=instance)
#     foodprogram_obj.day_set.all().delete()
#     return foodprogram_obj

# def get_product_qs(ck, instance):
#     product_qs = Product.objects.filter(recipe__recipe_appointment__name='Фитнес')
#     if ck < instance.dk:
#         product_qs = product_qs.filter(recipe__recipe_type__name='Похудеть')
#     return product_qs

# def get_day(foodprogram_obj, settings_day, i):
#     day_obj =  Day.objects.create(
#             foodprogram=foodprogram_obj,
#             name=settings_day.name,
#             sorting=i
#             )
#     return day_obj

# def get_settings_time(ck, j):
#     settings_times = (
#         ('08:00:00',0.3,'Завтрак','Десерты'),
#         ('11:00:00',0.1,'Перекус','Салаты'),
#         ('13:00:00',0.2,'Обед','Салаты'),
#         ('16:00:00',0.1,'Перекус','Добавки'),
#         ('18:00:00',0.2,'Ужин','Салаты'),
#         ('20:00:00',0.1,'Поздний ужин','Добавки'),
#         )
#     settings_times_min_kkal = (
#         ('08:00:00',0.3,'Завтрак','Десерты'),
#         ('11:00:00',0.1,'Перекус','Салаты'),
#         ('13:00:00',0.2,'Обед','Салаты'),
#         ('16:00:00',0.1,'Перекус','Добавки'),
#         ('18:00:00',0.2,'Ужин','Салаты'),
#         ('20:00:00',0.1,'Поздний ужин','Добавки'),
#         )
#     settings_time, kf, recipe_appointment, recipe_food_type = settings_times[j][0], settings_times[j][1], settings_times[j][2], settings_times[j][3]
#     if ck < 1300:
#         settings_time, kf, recipe_appointment, recipe_food_type = settings_times_min_kkal[j][0], settings_times_min_kkal[j][1], settings_times_min_kkal[j][2], settings_times_min_kkal[j][3]
#     settings_time_obj = SettingsTime.objects.get(name=settings_time)
#     return settings_time_obj, kf, recipe_appointment, recipe_food_type

# def get_time(j, settings_time_obj, day_obj):
#     try:
#         time_obj = Time.objects.create(number=j, settingstime=settings_time_obj, day=day_obj)
#     except Exception as e:
#         print(e)
#     return time_obj

# def get_time_kkal(ck, kf):
#     return ck*kf

# def get_filtered_main_product_qs(product_qs, recipe_appointment):
#     return product_qs.filter(recipe__recipe_appointment__name=recipe_appointment)

# def get_filtered_additional_product_qs(product_qs, recipe_food_type):
#     return product_qs.filter(recipe__recipe_food_type__name=recipe_food_type)

# def get_random_obj(product_qs):
#     qs_ids = product_qs.values_list('id', flat=True)
#     random_index = randrange(0, len(qs_ids))
#     product_obj = product_qs.get(id=qs_ids[random_index])
#     return product_obj

# def get_product_obj(product_qs, rest_kkal):
#     product_obj = get_random_obj(product_qs)
#     product_weight = product_obj.kbzu_1portion.weight
#     return product_obj, product_weight

# def get_product_kkal_sum(food_products):
#     product_sum = 0
#     for product in food_products:
#         product_sum += product.kbzu_1portion.kkal
#     return product_sum

# def check_product_kkal(filtered_product_qs, rest_kkal):
#     return filtered_product_qs.filter(kbzu_1portion__kkal__lte=rest_kkal).count() > 0

# def get_rest_kkal(current_kkal, time_kkal):
#     return time_kkal-current_kkal

# def get_current_kkal(food_products):
#     result = 0
#     for product, weight in food_products:
#         result += product.kbzu_1portion.kkal
#     return result

# def get_range_additional_weight(program_kf, settings_time_obj):
#     time = str(settings_time_obj.name)
#     if time == '20:00:00':
#         return 50, 400
#     else:
#         if program_kf == LOSEWEIGHT_KF:
#             return 130, 200
#         if program_kf == 1:
#             return 130, 200
#         if program_kf == FATTEN:
#             return 130, 250

# def get_range_main_weight(program_kf, settings_time_obj):
#     time = str(settings_time_obj.name)
#     if time == '08:00:00':
#         return 50, 400
#     if program_kf == LOSEWEIGHT_KF:
#         return 100, 180
#     if program_kf == 1:
#         return 100, 180
#     if program_kf == FATTEN:
#         return 100, 250

# def get_food_products(program_kf, ck, day_kkal, time_kkal, product_qs, settings_time_obj, recipe_appointment, recipe_food_type):
#     food_products = []
#     products_lst = []
#     current_kkal = 0

#     ######### 08:00 / 13:00 / 18:00 ###########
#     if recipe_appointment in ['Завтрак','Обед','Ужин']:
#         ## CHECK IF THERE ANY PRODUCTS WITH NEEDED KKAL TO BE ADDED AS ADDITIONAL PRODUCT
#         filtered_addidional_product_qs = get_filtered_additional_product_qs(product_qs, recipe_food_type=recipe_food_type)
#         rest_kkal = get_rest_kkal(current_kkal, time_kkal)
#         if check_product_kkal(filtered_addidional_product_qs, rest_kkal):
#             current_additional_kkal = 0
#             current_additional_weight = 0
#             product_obj = None
#             while product_obj not in products_lst:
#                 product_obj, product_weight = get_product_obj(filtered_addidional_product_qs, rest_kkal)
#                 if product_obj.kbzu_1portion.kkal > rest_kkal:
#                     continue

#                 ## CHECK FOR MIN KKAL AND MAX WEIGHT
#                 if product_obj not in products_lst:
#                     min_additional_weight, max_additional_weight = get_range_additional_weight(program_kf, settings_time_obj)
#                     while current_additional_weight < min_additional_weight:
#                         current_additional_weight += product_obj.kbzu_1portion.weight/2
#                         current_additional_kkal += product_obj.kbzu_1portion.kkal/2
#                         if current_additional_weight > max_additional_weight:
#                             return get_food_products(program_kf, ck, day_kkal, time_kkal, product_qs, settings_time_obj, recipe_appointment, recipe_food_type)

#                     current_kkal += current_additional_kkal
#                     product_weight = current_additional_kkal/product_obj.kbzu_1portion.kkal*product_obj.kbzu_1portion.weight
#                     food_products.append((product_obj, product_weight))
#                     products_lst.append(product_obj)


#         ## CHECK IF THERE ANY PRODUCTS WITH NEEDED KKAL TO BE ADDED AS MAIN PRODUCT
#         filtered_main_product_qs = get_filtered_main_product_qs(product_qs, recipe_appointment=recipe_appointment)
#         # print('!!!!!! LEN: {0}'.format(filtered_main_product_qs.count()))
#         rest_kkal = get_rest_kkal(current_kkal, time_kkal)
#         if check_product_kkal(filtered_main_product_qs, rest_kkal):
#             product_obj = None
#             while product_obj not in products_lst:
#                 product_obj, product_weight = get_product_obj(filtered_main_product_qs, rest_kkal)
#                 filtered_main_product_qs = filtered_main_product_qs.exclude(id=product_obj.id)
#                 # if filtered_main_product_qs.count() == 0:
#                 #     return get_food_products(program_kf, ck, day_kkal, time_kkal, product_qs, settings_time_obj, recipe_appointment, recipe_food_type)

#                 ## IF PRODUCT IN PRODUCTS ALREADY GET NEW ONE
#                 if product_obj not in products_lst:
#                     min_main_weight, max_main_weight = get_range_main_weight(program_kf, settings_time_obj)
#                     product_kkal = product_obj.kbzu_1portion.kkal
#                     # if not 0.4 <= product_kkal/rest_kkal <= 1:
#                     #     print('CONTINUE>>>>')
#                     #     continue
#                     main_kkal_sum = 0
#                     portion_number = 0
#                     product_weight = 0
#                     while main_kkal_sum < rest_kkal-product_kkal/5:
#                         main_kkal_sum += product_kkal/2
#                         product_weight += product_obj.kbzu_1portion.weight/2
#                         portion_number += product_weight/product_obj.kbzu_1portion.weight
#                         current_kkal += product_kkal/2

#                     if product_weight > max_main_weight:
#                         return get_food_products(program_kf, ck, day_kkal, time_kkal, product_qs, settings_time_obj, recipe_appointment, recipe_food_type)

#                     if product_weight < min_main_weight:
#                         return get_food_products(program_kf, ck, day_kkal, time_kkal, product_qs, settings_time_obj, recipe_appointment, recipe_food_type)

#                     food_products.append((product_obj, product_weight))
#                     products_lst.append(product_obj)
#         else:
#             return get_food_products(program_kf, ck, day_kkal, time_kkal, product_qs, settings_time_obj, recipe_appointment, recipe_food_type)

#     # ######### 11:00 / 16:00 / 20:00  ###########
#     if recipe_appointment in ['Перекус','Поздний ужин']:
#         combine_filtered_product_qs = get_filtered_main_product_qs(product_qs, recipe_appointment=recipe_appointment)|get_filtered_additional_product_qs(product_qs, recipe_food_type=recipe_food_type)
#         combine_filtered_product_qs = combine_filtered_product_qs.distinct()
#         rest_kkal = get_rest_kkal(current_kkal, time_kkal)

#         ## CHECK IF THERE ARE ANY PRODUCTS WITH NEEDED KKAL
#         if check_product_kkal(combine_filtered_product_qs, rest_kkal):
#             product_obj = None
#             while product_obj not in products_lst:
#                 product_obj, product_weight = get_product_obj(combine_filtered_product_qs, rest_kkal)

#                 ## IF PRODUCT IN PRODUCTS ALREADY GET NEW ONE
#                 if product_obj not in products_lst:
#                     product_kkal = product_obj.kbzu_1portion.kkal
#                     if not 0.4 <= product_kkal/rest_kkal <= 2:
#                         continue
#                     main_kkal_sum = 0
#                     portion_number = 0
#                     product_weight = 0
#                     while main_kkal_sum < rest_kkal-product_kkal/4:
#                         main_kkal_sum += product_kkal/2
#                         product_weight += product_obj.kbzu_1portion.weight/2
#                         portion_number += product_weight/product_obj.kbzu_1portion.weight
#                         current_kkal += product_kkal/2

#                     min_additional_weight, max_additional_weight = get_range_additional_weight(program_kf, settings_time_obj)
#                     if min_additional_weight < product_weight < max_additional_weight:
#                         food_products.append((product_obj, product_weight))
#                         products_lst.append(product_obj)
#                     else:
#                         return get_food_products(program_kf, ck, day_kkal, time_kkal, product_qs, settings_time_obj, recipe_appointment, recipe_food_type)

#     return food_products, get_current_kkal(food_products)

# def get_food(foodprogram_obj, day_obj, time_obj, product_obj, product_weight):
#     return Food.objects.create(
#         foodprogram=foodprogram_obj,
#         day=day_obj,
#         time=time_obj,
#         product=product_obj,
#         weight=product_weight,
#         kkal=product_obj.kbzu_1portion.kkal*product_weight/product_obj.kbzu_1portion.weight,
#         protein=product_obj.kbzu_1portion.protein*product_weight/product_obj.kbzu_1portion.weight,
#         fat=product_obj.kbzu_1portion.fat*product_weight/product_obj.kbzu_1portion.weight,
#         carbohydrate=product_obj.kbzu_1portion.carbohydrate*product_weight/product_obj.kbzu_1portion.weight,
#         )

# def get_snak2(snak1, snak2_time):
#     product_obj = list(snak1)[1]
#     return (snak2_time, product_obj)

# def get_evening(dinner, evening_time):
#     product_obj = list(dinner)[1]
#     return (evening_time, product_obj)

# def reorder_products_for_day(products_for_day):
#     snak1 = products_for_day[1] # GET BREAKFAST
#     dinner = products_for_day[2] # GET DINNER
#     snak2_time = products_for_day[3][0]
#     evening_time = products_for_day[4][0]
#     del products_for_day[3] # DEL SNAK2
#     del products_for_day[4] # DEL EVENING
#     snak2 = get_snak2(snak1, snak2_time)
#     evening = get_evening(dinner, evening_time)
#     products_for_day[3] = snak2 # ADD SNAK2 = SNAk1
#     products_for_day[4] = evening # ADD DINNER = EVENING
#     return products_for_day

# # CHECK IF DAY_KKAL IN RANGE OF + - 10% OF CK
# def is_kkal_in_range(products_for_day, ck):
#     day_kkal = 0
#     min_kkal = ck - ck/10
#     max_kkal = ck + ck/10
#     for key, values in products_for_day.items():
#         food_products = values[1]
#         for product_obj, product_weight in food_products:
#             day_kkal += product_weight/product_obj.kbzu_1portion.weight*product_obj.kbzu_1portion.kkal
#     if min_kkal < day_kkal < max_kkal:
#         # print('DAY_KKAL IS OK: {0} | {1} | {2} %'.format(day_kkal, ck, day_kkal/ck*100))
#         return True
#     # print('DAY_KKAL: {0} IS NOT IN RANGE: {1} %'.format(day_kkal, day_kkal/ck*100))
#     return False


# ########### BY TIME #############

# def get_fat_norm(instance, program_kf, kf):
#     weight = instance.weight
#     if program_kf == LOSEWEIGHT_KF:
#         fat_norm = weight*0.7
#     if program_kf == 1:
#         fat_norm = weight*1.3
#     if program_kf == FATTEN:
#         fat_norm = weight*2
#     return fat_norm*kf

# # CHECK IF DAY FAT IS LESS THAN +10% OF DAY FAT NORM
# def is_fat_in_range(food_products, instance, program_kf, kf):
#     food_fat = 0
#     for product_obj, product_weight in food_products:
#         food_fat += product_weight/product_obj.kbzu_1portion.weight*product_obj.kbzu_1portion.fat
#     instance_fat_norm = get_fat_norm(instance, program_kf, kf)
#     min_fat = instance_fat_norm*0.8
#     max_fat = instance_fat_norm*1.2

#     if food_fat < max_fat:
#         return True
#     return False

# def get_pro_norm(instance, program_kf, kf):
#     weight = instance.weight
#     if instance.training_level == 'N':
#         day_pro_norm = weight*1.2
#     if instance.training_level in ['M', 'A']:
#         day_pro_norm = weight*1.5
#     if instance.training_level == 'P':
#         day_pro_norm = weight*1.8
#     return day_pro_norm*kf

# def is_protein_in_range(food_products, instance, program_kf, kf):
#     food_pro = 0
#     for product_obj, product_weight in food_products:
#         food_pro += product_weight/product_obj.kbzu_1portion.weight*product_obj.kbzu_1portion.protein

#     instance_pro_norm = get_pro_norm(instance, program_kf, kf)
#     min_pro = instance_pro_norm*0.9
#     max_pro = instance_pro_norm*1.1

#     if min_pro < food_pro < max_pro:
#         return True
#     return False

# ########### BY DAY #################
# def get_day_pro_norm(instance, program_kf):
#     weight = instance.weight
#     if instance.training_level == 'N':
#         day_pro_norm = weight*1.2
#     if instance.training_level in ['M', 'A']:
#         day_pro_norm = weight*1.5
#     if instance.training_level == 'P':
#         day_pro_norm = weight*1.8
#     return day_pro_norm*program_kf

# def is_kbzu_in_range(instance, carbo, fat, pro, program_kf):
#     # CHECK PRO
#     instance_pro_day_norm = get_day_pro_norm(instance, program_kf)
#     min_pro = instance_pro_day_norm*0.8
#     max_pro = instance_pro_day_norm*1.2

#     # print(min_pro, pro, max_pro)

#     if min_pro < pro < max_pro:
#         return True
#     return False

# ########### END BY DAY #############

# def get_bzu(products_for_day):
#     carbo = 0
#     fat = 0
#     pro = 0
#     for time_obj, food_products in products_for_day:
#         for product_obj, product_weight in food_products:
#             carbo += product_weight/product_obj.kbzu_1portion.weight*product_obj.kbzu_1portion.carbohydrate
#             fat += product_weight/product_obj.kbzu_1portion.weight*product_obj.kbzu_1portion.fat
#             pro += product_weight/product_obj.kbzu_1portion.weight*product_obj.kbzu_1portion.protein
#     return carbo, fat, pro

# def make_time(products_for_day_tmp, day_obj):
#     products_for_day = []
#     # for settings_time, items in products_for_day_tmp:
#     #     food_products = items[0]
#     #     j = items[1]
#     #     for product_obj, product_weight in food_products:
#     #         time_obj                           = get_time(j, settings_time, day_obj)
#     #         products_for_day.append((time_obj, food_products))
#     # return products_for_day
#     # print('1')
#     for key, value in products_for_day_tmp.items():
#         settings_time_obj = value[0]
#         food_products = value[1]
#         time_obj = get_time(key, settings_time_obj, day_obj)
#         products_for_day.append((time_obj, food_products))
#     return products_for_day

# def get_products_for_day(i, settings_day, foodprogram_obj, ck, program_kf, product_qs):
#     day_kkal = 0
#     j = 0
#     products_for_day_tmp = {}
#     products_for_day = []
#     for j in range(0,6):
#         settings_time_obj, kf, recipe_appointment, recipe_food_type   = get_settings_time(ck, j)
#         time_kkal                          = get_time_kkal(ck, kf)
#         food_products, food_kkal           = get_food_products(program_kf, ck, day_kkal, time_kkal, product_qs, settings_time_obj, recipe_appointment, recipe_food_type)
#         # products_for_day_tmp.append((settings_time_obj, (food_products, j)))
#         products_for_day_tmp[j] = (settings_time_obj, food_products)
#         j+=1

#     # MAKE SIMPLE LIST OF PRODUCTS
#     if not preferences.AppSettings.various_food_generation_mode:
#         products_for_day_tmp = reorder_products_for_day(products_for_day_tmp)

#     # CHECK IF SUM OF DAY KKAL IS IN RANGE AND MAKE FOODS
#     if not is_kkal_in_range(products_for_day_tmp, ck):
#         return get_products_for_day(i, settings_day, foodprogram_obj, ck, program_kf, product_qs)


#     # if not is_fat_in_range(food_products, instance, program_kf, kf):
#     #     while is_fat_in_range(food_products, instance, program_kf, kf):
#     #         food_products, food_kkal   = get_food_products(program_kf, ck, day_kkal, time_kkal, product_qs, settings_time_obj, recipe_appointment, recipe_food_type)

#     # if not is_protein_in_range(food_products, instance, program_kf, kf):
#     #     while is_protein_in_range(food_products, instance, program_kf, kf):
#     #         food_products, food_kkal   = get_food_products(program_kf, ck, day_kkal, time_kkal, product_qs, settings_time_obj, recipe_appointment, recipe_food_type)

#     # ADD CURRENT TIME AND PRODUCTS TO LIST TO GATHER ALL PRODUCTS IN ONE LIST FOR DAY
#     day_obj = get_day(foodprogram_obj, settings_day, i)
#     products_for_day = make_time(products_for_day_tmp, day_obj)

#     # GET SUM OF KBZU
#     carbo, fat, pro = get_bzu(products_for_day)

#     return products_for_day, day_obj

# @shared_task
# def foodprogram_generator(pk, flag):
#     if flag == 'leaduser':
#         instance = LeadUser.objects.get(id=pk)
#     elif flag == 'client':
#         instance = Client.objects.get(id=pk)
#     else:
#         return

#     for i in CK_PROGRAM_NAME:
#         program_kf = i[0]
#         ck = instance.dk*program_kf
#         program_name = i[1]
#         program_obj = Program.objects.get(name=program_name)
#         foodprogram_obj                 = get_foodprogram(program_obj, instance)
#         product_qs                      = get_product_qs(ck, instance)
#         i=0
#         settings_days = list(SettingsDay.objects.all())
#         while i < len(settings_days):
#             settings_day = settings_days[i]
#             products_for_day, day_obj = get_products_for_day(i, settings_day, foodprogram_obj, ck, program_kf, product_qs)
#             for time_obj, food_products in products_for_day:
#                 for product_obj, product_weight in food_products:
#                     food_obj            = get_food(foodprogram_obj, day_obj, time_obj, product_obj, product_weight)
#             i+=1
#     return

# def get_client_id_from_celery():
#     try:
#         running_tasks = inspect().active().values()
#         client_args = list(running_tasks)[0][0]['args']
#         return int(client_args.split(',')[0].replace('(',''))
#     except Exception as e:
#         return 0

# def running_tasks_by_client(instance):
#     task_client_id = get_client_id_from_celery()
#     if task_client_id == instance.id:
#         return True
#     return False

# @receiver(post_save, sender=Client)
# def generate_food_post_save(instance, **kwargs):

#     if kwargs['created']:
#         try:
#             leaduser_obj = instance.leaduser
#             foodprograms = leaduser_obj.foodprogram_set.all()
#             for foodprogram in foodprograms:
#                 foodprogram.client = instance
#                 foodprogram.save()
#         except Exception as e:
#             flag = 'client'
#             foodprogram_generator.delay(instance.id, flag)

#         # SEND MESSAGE ABOUT NEW CLIENT
#         try:
#             boss_trainer = Trainer.objects.get(is_boss=True)
#             title = 'Новый клиент'
#             message = 'Зарегистрирован новый клиент: {0}'.format(instance.user.get_full_name())
#             from_mail = 'nasporte.online@gmail.com'
#             to_mail = boss_trainer.user.email
#             emails = (
#                 (
#                     title,
#                     message,
#                     from_mail,
#                     [to_mail]
#                     ),
#                 )
#             results = mail.send_mass_mail(emails)
#             return results
#         except Exception as e:
#             print(e)
#     else:
#         if instance.regenerate_food:
#             instance.regenerate_food = False
#             instance.save()
#             if not running_tasks_by_client(instance):
#                 instance.foodprogram_set.all().delete()
#                 flag = 'client'
#                 foodprogram_generator.delay(instance.id, flag)
#     return


# @receiver(post_save, sender=LeadUser)
# def leaduser_foodprogram_post_save(instance, **kwargs):
#     if kwargs['created']:
#         flag = 'leaduser'
#         # foodprogram_generator(instance.id, flag)
#         foodprogram_generator.delay(instance.id, flag)

#         # instance.new_messages_from_client = True
#         instance.save()

#         # SEND MESSAGE ABOUT NEW LEAD
#         boss_trainer = Trainer.objects.get(is_boss=True)
#         title = 'Новый лид №{0}'.format(instance.id)
#         message = 'Зарегистрирован новый лид №{0}'.format(instance.id)
#         from_mail = 'nasporte.online@gmail.com'
#         to_mail = boss_trainer.user.email
#         emails = (
#             (
#                 title,
#                 message,
#                 from_mail,
#                 [to_mail]
#                 ),
#             )
#         return mail.send_mass_mail(emails)
#     return

### FOOD GENERATOR 2.0
LOSEWEIGHT_KF = 0.7
HEALTH_KF = 1
FATTEN_KF = 1.2

CK_PROGRAM_NAME = (
    ('LOSEWEIGHT',LOSEWEIGHT_KF,'Программа питания для похудения'),
    ('HEALTH',HEALTH_KF,'Здоровое питание'),
    ('FATTEN',FATTEN_KF,'Программа питания для набора массы'),
    )

TIMES = [
    '08:00:00',
    '11:00:00',
    '13:00:00',
    '16:00:00',
    '18:00:00',
    '20:00:00',
]

PORTIONS = {
    '08:00:00':{
        'portion_range':{
            'LOSEWEIGHT':{
                'main_product':(80,400),
                'additional_product':(130,200),
            },
            'HEALTH':{
                'main_product':(100,400),
                'additional_product':(130,200),
            },
            'FATTEN':{
                'main_product':(100,400),
                'additional_product':(130,250),
            },
        },
        'food_types':('Завтрак','Десерты'),
        'food_time_kf':0.3,
    },
    '11:00:00':{
        'portion_range':{
            'LOSEWEIGHT':{
                'main_product':(100,180),
                'additional_product':(130,200),
            },
            'HEALTH':{
                'main_product':(100,180),
                'additional_product':(130,200),
            },
            'FATTEN':{
                'main_product':(200,250),
                'additional_product':(130,250),
            },
        },
        'food_types':('Перекус','Салаты'),
        'food_time_kf':0.1,
    },
    '13:00:00':{
        'portion_range':{
            'LOSEWEIGHT':{
                'main_product':(100,180),
                'additional_product':(130,200),
            },
            'HEALTH':{
                'main_product':(100,180),
                'additional_product':(130,200),
            },
            'FATTEN':{
                'main_product':(200,250),
                'additional_product':(130,250),
            },
        },
        'food_types':('Обед','Салаты'),
        'food_time_kf':0.2,
    },
    '16:00:00':{
        'portion_range':{
            'LOSEWEIGHT':{
                'main_product':(100,180),
                'additional_product':(130,200),
            },
            'HEALTH':{
                'main_product':(100,180),
                'additional_product':(130,200),
            },
            'FATTEN':{
                'main_product':(200,250),
                'additional_product':(130,250),
            },
        },
        'food_types':('Перекус','Салаты'),
        'food_time_kf':0.1,
    },
    '18:00:00':{
        'portion_range':{
            'LOSEWEIGHT':{
                'main_product':(100,180),
                'additional_product':(130,200),
            },
            'HEALTH':{
                'main_product':(100,180),
                'additional_product':(130,200),
            },
            'FATTEN':{
                'main_product':(200,250),
                'additional_product':(130,250),
            },
        },
        'food_types':('Ужин','Салаты'),
        'food_time_kf':0.2,
    },
    '20:00:00':{
        'portion_range':{
            'LOSEWEIGHT':{
                'main_product':(100,180),
                'additional_product':(50,400),
            },
            'HEALTH':{
                'main_product':(100,180),
                'additional_product':(50,400),
            },
            'FATTEN':{
                'main_product':(200,250),
                'additional_product':(50,400),
            },
        },
        'food_types':('Поздний ужин','Добавки'),
        'food_time_kf':0.1,
    },
}


def get_portions(PORTIONS, food_time, program_type):
    main_product_portions = PORTIONS[food_time]['portion_range'][program_type]['main_product']
    additional_product_portions = PORTIONS[food_time]['portion_range'][program_type]['additional_product']
    food_types = PORTIONS[food_time]['food_types']
    food_time_kf = PORTIONS[food_time]['food_time_kf']
    return main_product_portions, additional_product_portions, food_types, food_time_kf

def get_food_time_kf(PORTIONS, food_time):
    return PORTIONS[food_time]['food_time_kf']

def get_product_qs(ck, instance):
    all_product_qs = Product.objects.all()
    product_qs = all_product_qs.filter(recipe__recipe_appointment__name='Фитнес')
    if ck < instance.dk:
        product_qs = all_product_qs.filter(recipe__recipe_type__name='Похудеть')
    return product_qs


def get_random_id(qs_ids):
    random_item_index = randrange(0, len(qs_ids))
    return qs_ids[random_item_index]


def get_kkal_to_eat(ck_kkal, food_time_kf, food_time):
    kkal_to_eat = ck_kkal * food_time_kf / 2
    if food_time in ['11:00:00','16:00:00','20:00:00']:
        kkal_to_eat = ck_kkal * food_time_kf
    return kkal_to_eat

def find_product(main_product_qs, ck_kkal, food_time_kf, food_time, product_portions, products_in_week):

    ## FIND THE PRODUCT PRODUCTS WITH NEEDED KKALS
    qs_ids = list(main_product_qs.values_list('id', flat=True))
    lst = []
    while len(qs_ids) > 0:
        random_id = get_random_id(qs_ids)
        product_obj = main_product_qs.get(id=random_id)
        qs_ids.remove(random_id)
        kkal_to_eat = get_kkal_to_eat(ck_kkal, food_time_kf, food_time)
        kkal_in_100g = product_obj.kbzu_100g.kkal
        weight_to_eat = kkal_to_eat / kkal_in_100g * 100
        min_portion = int(product_portions[0])
        max_portion = int(product_portions[1])
        if min_portion < weight_to_eat < max_portion:
            if product_obj in products_in_week:
                lst.append(product_obj.id)
                continue
            else:
                # print('GET EXACT')
                return product_obj

    if len(lst) > 0:
        random_id = get_random_id(lst)
        # print('GET RANDOM')
        return Product.objects.get(id=random_id)

    # print('GET THE LAST ')
    return product_obj


def get_product(ck_kkal,food_time, product_portions, food_types, food_time_kf, instance, main_products_in_week, additional_products_in_week, trigger):

    ## GET ALL NEEDED PRODUCTS
    product_qs = get_product_qs(ck_kkal, instance)
    if trigger == 'main_product':
        main_product_qs = product_qs.filter(recipe__recipe_appointment__name=food_types[0])
        product_obj = find_product(main_product_qs, ck_kkal, food_time_kf, food_time, product_portions, main_products_in_week)
    if trigger == 'additional_product':
        main_product_qs = product_qs.filter(recipe__recipe_food_type__name=food_types[1])
        product_obj = find_product(main_product_qs, ck_kkal, food_time_kf, food_time, product_portions, additional_products_in_week)

    return product_obj


def get_food_kbzu(product_obj, ck_kkal, food_time_kf, food_time):
    kkal_to_eat = get_kkal_to_eat(ck_kkal, food_time_kf, food_time)
    kkal_in_100g = product_obj.kbzu_100g.kkal
    weight_to_eat = kkal_to_eat / kkal_in_100g * 100
    protein = weight_to_eat / 100 * product_obj.kbzu_100g.protein
    fat = weight_to_eat / 100 * product_obj.kbzu_100g.fat
    carbohydrate = weight_to_eat / 100 * product_obj.kbzu_100g.carbohydrate
    return weight_to_eat, kkal_to_eat, protein, fat, carbohydrate

def create_food(time, product, foodprogram, day, kkal, weight_to_eat, protein, fat, carbohydrate):
    return Food.objects.create(
        foodprogram=foodprogram,
        day=day,
        time=time,
        product=product,
        weight=weight_to_eat,
        kkal=kkal,
        protein=protein,
        fat=fat,
        carbohydrate=carbohydrate,
        )


def get_reversed(products_for_food):
    lst = []
    for i in reversed(products_for_food):
        lst.append(i)
    return lst


def foodprogram_generator(instance, flag):
    if 'leaduser' in flag:
        leaduser = instance
        client = None
    if 'client' in flag:
        leaduser = None
        client = instance

    days = list(SettingsDay.objects.all())

    for program_type, kf, program_name in CK_PROGRAM_NAME:
        ck_kkal = instance.dk * kf
        program = Program.objects.get(name=program_name)

        ## CREATE FOODPROGRAM
        foodprogram = FoodProgram.objects.create(
            program=program,
            leaduser=leaduser,
            client=client,
            )

        ## MAKE DAYS
        additional_products_in_week = []
        main_products_in_week = []
        for i in range(0,len(days)):
            day = Day.objects.create(
                foodprogram=foodprogram,
                sorting=i,
                name=days[i].name,
                )
            products_in_time = {}
            for food_time in reversed(TIMES):
                main_product_portions, additional_product_portions, food_types, food_time_kf = get_portions(PORTIONS, food_time, program_type)

                ## GET ADDITIONAL FOOD
                trigger = 'additional_product'
                if food_time in '20:00:00':
                    trigger = 'main_product'
                aditional_product_obj = get_product(ck_kkal,food_time, additional_product_portions, food_types, food_time_kf, instance,main_products_in_week, additional_products_in_week, trigger=trigger)
                additional_products_in_week.append(aditional_product_obj)

                ## GET MAIN FOOD
                if food_time in ['11:00:00','16:00:00','20:00:00']:
                    main_product_obj = None
                else:
                    main_product_obj = get_product(ck_kkal,food_time, main_product_portions, food_types, food_time_kf, instance, main_products_in_week, additional_products_in_week, trigger='main_product')
                main_products_in_week.append(main_product_obj)
                products_in_time[food_time] = (aditional_product_obj, main_product_obj)

            ## REPLACE PRODUCTS BY TIME (13 = 18, 11 = 16)
            products_for_food = []
            products_for_food.append(('08:00:00', products_in_time['08:00:00']))
            products_for_food.append(('11:00:00', products_in_time['11:00:00']))
            products_for_food.append(('13:00:00', products_in_time['13:00:00']))
            products_for_food.append(('16:00:00', products_in_time['11:00:00']))
            products_for_food.append(('18:00:00', products_in_time['13:00:00']))
            products_for_food.append(('20:00:00', products_in_time['20:00:00']))

            # products_for_food = get_reversed(products_for_food)
            for i in range(0,len(products_for_food)):
                time = products_for_food[i][0]
                products = products_for_food[i][1]
                settingstime = SettingsTime.objects.get(name=time)
                time_obj = Time.objects.create(
                    number=i,
                    settingstime=settingstime,
                    day=day,
                    )
                aditional_product_obj = products[0]
                food_time_kf = get_food_time_kf(PORTIONS, time)
                weight_to_eat, kkal, protein, fat, carbohydrate = get_food_kbzu(aditional_product_obj,ck_kkal, food_time_kf, time)
                create_food(time_obj, aditional_product_obj, foodprogram, day, kkal, weight_to_eat, protein, fat, carbohydrate)

                main_product_obj = products[1]
                if main_product_obj != None:
                    weight_to_eat, kkal, protein, fat, carbohydrate = get_food_kbzu(main_product_obj,ck_kkal, food_time_kf, time)
                    create_food(time_obj, main_product_obj, foodprogram, day, kkal, weight_to_eat, protein, fat, carbohydrate)


    return


@receiver(post_save, sender=LeadUser)
def leaduser_foodprogram_post_save(instance, **kwargs):
    if kwargs['created']:
        flag = 'leaduser'
        foodprogram_generator(instance, flag)

        # instance.new_messages_from_client = True
        instance.save()

        # SEND MESSAGE ABOUT NEW LEAD
        boss_trainer = Trainer.objects.get(is_boss=True)
        title = 'Новый лид №{0}'.format(instance.id)
        message = 'Зарегистрирован новый лид №{0}'.format(instance.id)
        from_mail = 'nasporte.online@gmail.com'
        to_mail = boss_trainer.user.email
        emails = (
            (
                title,
                message,
                from_mail,
                [to_mail]
                ),
            )
        return mail.send_mass_mail(emails)
    return


@receiver(post_save, sender=Client)
def generate_food_post_save(instance, **kwargs):

    if kwargs['created']:
        try:
            leaduser_obj = instance.leaduser
            foodprograms = leaduser_obj.foodprogram_set.all()
            for foodprogram in foodprograms:
                foodprogram.client = instance
                foodprogram.save()
        except Exception as e:
            flag = 'client'
            foodprogram_generator(instance.id, flag)

        # SEND MESSAGE ABOUT NEW CLIENT
        try:
            boss_trainer = Trainer.objects.get(is_boss=True)
            title = 'Новый клиент'
            message = 'Зарегистрирован новый клиент: {0}'.format(instance.user.get_full_name())
            from_mail = 'nasporte.online@gmail.com'
            to_mail = boss_trainer.user.email
            emails = (
                (
                    title,
                    message,
                    from_mail,
                    [to_mail]
                    ),
                )
            results = mail.send_mass_mail(emails)
            return results
        except Exception as e:
            print(e)
    else:
        if instance.regenerate_food:
            instance.regenerate_food = False
            instance.save()
            instance.foodprogram_set.all().delete()
            flag = 'client'
            foodprogram_generator(instance, flag)
    return


