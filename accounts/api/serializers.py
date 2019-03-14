# -*- coding: utf-8 -*-
from rest_framework.reverse import reverse as api_reverse
from rest_framework import routers, serializers
from rest_framework import validators
from chat.models import ChatMessage, Thread
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.hashers import make_password
from accounts.models import (
    Client,
    Day,
    ExerciseComment,
    Food,
    Food,
    FoodProgram,
    LeadUser,
    Message,
    Progress,
    Time,
    Trainer,
    Training,
    Workout,
    WorkoutComment,
    Wset,
    PersonalWorkoutProfile,
    PersonalNutrimentProfile,
    )
from appsettings.models import (
    SEX,
    LEVELS,
    )
from options.api.serializers import CompetitionSerializer, MuscleSerializer, ProductSerializer, FitnessClubSerializer
from options.models import Exercise, Product, FitnessClub
from partners.models import Promo, Partner
from subscriptions.models import (
    Program,
    Category,
    Favourite,
    )
from django.contrib.auth.models import User, Group
from memberzone.models import Order
from preferences import preferences
import datetime, re


today = datetime.date.today()


########################################################################################################################
## PROGRESS CRUD

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = [
            'id',
            'client',
            'image1',
            'image2',
            'image3',
            'current_weight',
            'chest',
            'waistline',
            'hip',
            'leg',
            'created',
            'updated',
        ]


########################################################################################################################
## TRAINERS

class BossTrainerSerializer(serializers.ModelSerializer):
    first_name = serializers.PrimaryKeyRelatedField(source='user.first_name', read_only=True)
    last_name = serializers.PrimaryKeyRelatedField(source='user.last_name', read_only=True)
    class Meta:
        model = Trainer
        fields = [
            'id',
            'user',
            'first_name',
            'last_name',
            'avatar',
            'is_boss',
            'city',
            'content',
            'phone',
            'skype',
            'whatsapp',
            'vk',
            'ok',
            'instagram',
            'fb',
            'yt',
            'promo_video',
            'image1',
            'image2',
            'image3',
            'image4',
            'image5',
            'image6',
            'created',
            'updated',
        ]


########################################################################################################################
## CHAT


class LeadUserNewMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadUser
        fields = [
            'new_messages_from_trainer',
            'new_messages_from_client',
        ]


class ClientNewMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'new_messages_from_trainer',
            'new_messages_from_client',
        ]



########################################################################################################################
## WORKOUT

class WorkoutCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutComment
        fields = [
            'id',
            'client',
            'workout',
            'content',
            'name_id',
            'created',
            'updated',
        ]

class ExerciseCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseComment
        fields = [
            'id',
            'client',
            'workout',
            'exercise',
            'name_id',
            'content',
            'created',
            'updated',
        ]

class ExerciseSerializer(serializers.ModelSerializer):
    muscles = MuscleSerializer(read_only=True, many=True)
    other_muscles = MuscleSerializer(read_only=True, many=True)
    video_thumb = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Exercise
        fields = [
            'id',
            'name',
            'content',
            'video',
            'short_video',
            'created',
            'updated',
            'muscles',
            'other_muscles',
            'video_thumb',
        ]

    def get_video_thumb(self, obj):
        data = {}
        try:
            video_code = obj.short_video.split('?v=')[1]
        except:
            video_code = obj.short_video.split('/')[-1]
        data['thumb'] = 'https://img.youtube.com/vi/{0}/mqdefault.jpg'.format(video_code)
        return data


class TrainingSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    class Meta:
        model = Training
        fields = [
            'id',
            'content',
            'created',
            'updated',
            'exercise'
        ]


class WsetSerializer(serializers.ModelSerializer):
    training_set = TrainingSerializer(read_only=True, many=True)
    rest_time = serializers.PrimaryKeyRelatedField(source='rest_time.name', read_only=True)
    class Meta:
        model = Wset
        fields = [
            'id',
            'number',
            'approach_number',
            'rest_time',
            'content',
            'created',
            'updated',
            'training_set'
        ]

class WorkoutSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api-accounts:workout_detail_api',
        lookup_field='pk',
        )
    wset_set = WsetSerializer(read_only=True, many=True)
    video_thumb = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Workout
        fields = [
            'id',
            'url',
            'number',
            'name',
            'video_thumb',
            'content',
            'sex',
            'training_level',
            'rest',
            'is_finished',
            'date',
            'created',
            'updated',
            'wset_set'
        ]

    def get_video_thumb(self, obj):
        data = {}
        lst = []
        request = self.context.get('request')
        scheme = request.scheme
        host = request.META['HTTP_HOST']
        for wset in obj.wset_set.all():
            for training in wset.training_set.all():
                    lst.append(training.exercise)
        try:
            exercise_obj = lst[0]
            try:
                video_code = exercise_obj.short_video.split('?v=')[1]
            except:
                video_code = exercise_obj.short_video.split('/')[-1]

            video_thumb =  'https://img.youtube.com/vi/{0}/mqdefault.jpg'.format(video_code)
        except:
            video_thumb = '{0}://{1}/media/programs/program_bg.png'.format(scheme, host)
        return video_thumb


class WorkoutIdSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api-accounts:workout_detail_api',
        lookup_field='pk',
        )
    class Meta:
        model = Workout
        fields = [
            'id',
            'url',
        ]
########################################################################################################################
## FOOD

class FoodSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    portion = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Food
        fields = [
            'id',
            'product',
            'weight',
            'kkal',
            'weight',
            'protein',
            'fat',
            'carbohydrate',
            'portion',
            'created',
            'updated',
        ]

    def get_portion(self, obj):
        return obj.get_portion_numbers()


class TimeSerializer(serializers.ModelSerializer):
    food_set = FoodSerializer(read_only=True, many=True)
    time = serializers.PrimaryKeyRelatedField(source='settingstime.name', read_only=True)
    class Meta:
        model = Time
        fields = [
            'id',
            'time',
            'weight',
            'kkal',
            'weight',
            'protein',
            'fat',
            'carbohydrate',
            'created',
            'updated',
            'food_set'
        ]
    def get_portion(self, obj):

        return

class DaySerializer(serializers.ModelSerializer):
    time_set = TimeSerializer(read_only=True, many=True)
    day_kbzu = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Day
        fields = [
            'id',
            'name',
            'sorting',
            'created',
            'updated',
            'time_set',
            'day_kbzu'
        ]

    def get_day_kbzu(self, obj):
        kkal = 0
        protein = 0
        fat = 0
        carbohydrate = 0
        for time in obj.time_set.all():
            kkal += time.kkal
            protein += time.protein
            fat += time.fat
            carbohydrate += time.carbohydrate
        return (
            {'kkal':kkal},
            {'protein':protein},
            {'fat':fat},
            {'carbohydrate':carbohydrate},
            )


class FoodProgramIdSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api-accounts:foodprogram_detail_api',
        lookup_field='pk',
        )
    class Meta:
        model = FoodProgram
        fields = [
            'id',
            'url',
        ]


class FoodProgramSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api-accounts:foodprogram_detail_api',
        lookup_field='pk',
        )
    day_set = DaySerializer(read_only=True, many=True)
    class Meta:
        model = FoodProgram
        fields = [
            'id',
            'url',
            'name',
            'content',
            'program',
            'created',
            'updated',
            'day_set'
        ]

class ClientFoodProgramUpdateSerializer(serializers.ModelSerializer):
    src_login = serializers.CharField(write_only=True)
    class Meta:
        model = Client
        fields = [
            'src_login',
        ]

    def create(self, validated_data):
        validated_data.pop('src_login', None)

########################################################################################################################
## LEADUSER

class LeadUserSerializer(serializers.ModelSerializer):
    foodprogram_set = FoodProgramSerializer(read_only=True, many=True)
    class Meta:
        model = LeadUser
        fields = [
            'id',
            'uuid',
            'chatid',
            'is_banned',
            'age',
            'high',
            'weight',
            'wish_weight',
            'sex',
            'training_level',
            'foodprogram_set',
            # 'messages',
            'created',
            'updated',
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                obj = LeadUser.objects.create(**validated_data)
        except Exception as e:
            raise serializers.ValidationError(e)
        return obj


class LeadUserMessageSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = LeadUser
        fields = [
            'messages',
        ]

    def get_trainer(self, message):
        name = message.trainer.user.first_name
        last_name = message.trainer.user.last_name
        return '{0}{1}'.format(name, last_name)


    def get_messages(self, obj):
        messages = ChatMessage.objects.none()
        trainer = Trainer.objects.get(is_boss=True)
        thread_qs = Thread.objects.filter(leaduser=obj, trainer=trainer)
        if thread_qs.exists():
            thread_obj = thread_qs[0]
            messages = thread_obj.chatmessage_set.order_by('-timestamp')[:300]

        data = {}
        for message in messages:
            message_item = {}
            message_item['thread'] = message.thread.id
            if message.trainer:
                message_item['trainer'] = self.get_trainer(message)
            message_item['leaduser'] = message.leaduser.id
            message_item['message'] = message.message
            message_item['userhandle'] = message.userhandle
            message_item['timestamp'] = message.timestamp
            data[message.id] = message_item
        return data


class CategorySerializer(serializers.ModelSerializer):
    program_type = serializers.SerializerMethodField(read_only=True)
    program_count = serializers.SerializerMethodField(read_only=True)
    program_id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Category
        fields = [
            'id',
            'parent_category',
            'name',
            'img',
            'desc',
            'rating',
            'program_type',
            'program_count',
            'program_id',
        ]

    def get_program_type(self, obj):
        return obj.program_set.all().first().program_type

    def get_program_count(self, obj):
        return obj.program_set.all().count()

    def get_program_id(self, obj):
        category_programs = obj.program_set.all()
        if category_programs.count() == 1:
            program_id = category_programs.first().id
        else:
            program_id = None
        return program_id


class ProgramSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
            view_name='api-accounts:program_detail_api',
            lookup_field='pk',
            )
    category = CategorySerializer(read_only=True, many=True)
    workouts = serializers.SerializerMethodField(read_only=True)
    foodprograms = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Program
        fields = [
            'id',
            'img',
            'video',
            'url',
            'is_active',
            'demo',
            'name',
            'short_desc',
            'desc',
            'program_type',
            'category',
            'rating',
            'recommend',
            'to_all',
            'daily',
            'workouts',
            'chargeable',
            'foodprograms',
            'created',
            'updated',
        ]


    def get_video_thumb(self, workout):
        data = {}
        lst = []
        request = self.context.get('request')
        scheme = request.scheme
        host = request.META['HTTP_HOST']
        for wset in workout.wset_set.all():
            for training in wset.training_set.all():
                    lst.append(training.exercise)
        try:
            exercise_obj = lst[0]
            try:
                video_code = exercise_obj.short_video.split('?v=')[1]
            except:
                video_code = exercise_obj.short_video.split('/')[-1]

            video_thumb =  'https://img.youtube.com/vi/{0}/mqdefault.jpg'.format(video_code)
        except:
            video_thumb = '{0}://{1}/media/programs/program_bg.png'.format(scheme, host)
        return video_thumb

    def get_workouts(self, obj):
        workouts = obj.workout_set.all()
        data = []
        if obj.program_type == 'WP':
            workouts = workouts.filter(program__program_type='WP')
        elif obj.program_type == 'WG':
            workouts = workouts.filter(program__program_type='WG').filter(date__month=today.month)
        elif obj.program_type == 'WC':
            workouts = workouts.filter(program__program_type='WC')

        for workout in workouts:
            workout_dict = {}
            workout_dict['id'] = str(workout.id)
            workout_dict['url'] = api_reverse('api-accounts:workout_detail_api', kwargs={'pk':workout.id})
            workout_dict['number'] = workout.number
            workout_dict['name'] = workout.name
            workout_dict['content'] = workout.content
            workout_dict['sex'] = workout.sex
            workout_dict['training_level'] = workout.training_level
            workout_dict['date'] = workout.date
            workout_dict['video_thumb'] = self.get_video_thumb(workout)
            workout_dict['rest'] = workout.is_rest()
            data.append(workout_dict)

        return data

    def get_foodprograms(self, obj):
        foodprograms = obj.foodprogram_set.all()
        data = []
        if obj.program_type == 'FP':
            foodprograms = foodprograms.filter(program__program_type='FP')
        elif obj.program_type == 'FG':
            foodprograms = foodprograms.filter(program__program_type='FG')

        for foodprogram in foodprograms:
            if not foodprogram.food_set.all().count() > 0:
                continue
            foodprogram_dict = {}
            foodprogram_dict['id'] = str(foodprogram.id)
            foodprogram_dict['url'] = api_reverse('api-accounts:foodprogram_detail_api', kwargs={'pk':foodprogram.id})
            foodprogram_dict['number'] = foodprogram.number
            foodprogram_dict['name'] = foodprogram.name
            foodprogram_dict['content'] = foodprogram.content
            data.append(foodprogram_dict)

        return data


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = [
            'id',
            'program',
            'client',
            'created',
            'updated',
        ]

    ## CREATE FAVOURITE OBJECT
    def create(self, validated_data):
        program_obj = validated_data['program']
        client_obj = validated_data['client']
        try:
            if not Favourite.objects.filter(program=program_obj, client=client_obj).first():
                fabourite_obj = Favourite.objects.create(program=program_obj, client=client_obj)
            else:
                raise serializers.ValidationError('Object is already exists')
        except Exception as e:
            raise serializers.ValidationError(e.args[0])
        return fabourite_obj

class FavouriteDetailSerializer(serializers.ModelSerializer):
    program = ProgramSerializer(read_only=True)
    class Meta:
        model = Favourite
        fields = [
            'id',
            'program',
            'client',
            'created',
            'updated',
        ]


class PersonalWorkoutProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalWorkoutProfile
        fields = [
            'id',
            'client',
            'country',
            'city',
            'disease',
            'purpose',
            'created',
            'updated',
        ]


class PersonalNutrimentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalNutrimentProfile
        fields = [
            'id',
            'client',
            'daily_regime',
            'training_days',
            'allergy',
            'product_excepts_info',
            'product_accept',
            'created',
            'updated',
        ]


class ClientSerializer(serializers.ModelSerializer):
    marafons = serializers.SerializerMethodField(read_only=True)
    personal_workout_profile = serializers.HyperlinkedRelatedField(
        source = 'personalworkoutprofile',
        read_only=True,
        lookup_field ='pk',
        view_name='api-accounts:personal_workout_profile',
    )
    personal_nutriment_profile = serializers.HyperlinkedRelatedField(
        source = 'personalnutrimentprofile',
        read_only=True,
        lookup_field ='pk',
        view_name='api-accounts:personal_nutriment_profile',
    )
    progress_set = ProgressSerializer(read_only=True, many=True)
    personal_workouts = serializers.SerializerMethodField(read_only=True)
    personal_foodprograms = serializers.SerializerMethodField(read_only=True)
    foodprogram_set = serializers.SerializerMethodField(read_only=True)
    favourite_set = FavouriteDetailSerializer(read_only=True, many=True)
    first_name = serializers.PrimaryKeyRelatedField(source='user.first_name', read_only=True)
    last_name = serializers.PrimaryKeyRelatedField(source='user.last_name', read_only=True)
    class Meta:
        model = Client
        fields = [
            'id',
            'uuid',
            'user',
            'first_name',
            'last_name',
            'patronymic',
            'phone',
            'slug',
            'age',
            'sex',
            'training_level',
            'high',
            'weight',
            'wish_weight',
            'avatar',
            'is_banned',
            'is_member',
            'workout_profile_completed',
            'personal_workout_profile',
            'nutriment_profile_completed',
            'personal_nutriment_profile',
            'progress_set',
            'personal_workouts',
            'personal_foodprograms',
            'foodprogram_set',
            'favourite_set',
            'marafons',
            'created',
            'updated',
        ]

    def get_marafons(self, obj):
        marafon_qs = obj.programs.filter(program_type='MT')
        data = {}
        for program in marafon_qs:
            data[program.id] = str(program.name)
        return [data]

    def get_personal_workouts(self, obj):
        personal_workouts_qs = obj.workout_set.filter(program__program_type='WP').filter(created__month=today.month)
        data = []
        for workout in personal_workouts_qs:
            workout_dict = {}
            workout_dict['id'] = str(workout.id)
            workout_dict['is_finished'] = workout.is_finished
            workout_dict['number'] = workout.number
            workout_dict['name'] = workout.name
            workout_dict['content'] = workout.content
            workout_dict['sex'] = workout.sex
            workout_dict['training_level'] = workout.training_level
            workout_dict['rest'] = workout.rest
            workout_dict['program_type'] = 'WP'
            workout_dict['url'] = api_reverse('api-accounts:workout_detail_api', kwargs={'pk':workout.id})
            workout_dict['created'] = workout.created
            data.append(workout_dict)

        return data


    def get_personal_foodprograms(self, obj):
        personal_foodprograms_qs = obj.foodprogram_set.filter(program__program_type='FP')
        data = []
        for foodprogram in personal_foodprograms_qs:
            foodprogram_dict = {}
            foodprogram_dict['id'] = str(foodprogram.id)
            foodprogram_dict['url'] = api_reverse('api-accounts:foodprogram_detail_api', kwargs={'pk':foodprogram.id})
            foodprogram_dict['number'] = foodprogram.number
            foodprogram_dict['name'] = foodprogram.name
            foodprogram_dict['content'] = foodprogram.content
            foodprogram_dict['program_type'] = 'FP'
            data.append(foodprogram_dict)

        return data

    def get_foodprogram_set(self, obj):
        foodprograms = obj.foodprogram_set.filter(program__program_type='FG')
        data = []

        for foodprogram in foodprograms:
            foodprogram_dict = {}
            foodprogram_dict['id'] = str(foodprogram.id)
            foodprogram_dict['url'] = api_reverse('api-accounts:foodprogram_detail_api', kwargs={'pk':foodprogram.id})
            foodprogram_dict['number'] = foodprogram.number
            foodprogram_dict['name'] = foodprogram.name
            foodprogram_dict['content'] = foodprogram.content
            foodprogram_dict['program'] = foodprogram.program.id
            data.append(foodprogram_dict)

        return data


class ClientShortSerializer(serializers.ModelSerializer):
    personal_workout_profile = serializers.HyperlinkedRelatedField(
        source = 'personalworkoutprofile',
        read_only=True,
        lookup_field ='pk',
        view_name='api-accounts:personal_workout_profile',
    )
    personal_nutriment_profile = serializers.HyperlinkedRelatedField(
        source = 'personalnutrimentprofile',
        read_only=True,
        lookup_field ='pk',
        view_name='api-accounts:personal_nutriment_profile',
    )
    favourite_set = FavouriteDetailSerializer(read_only=True, many=True)
    first_name = serializers.PrimaryKeyRelatedField(source='user.first_name', read_only=True)
    last_name = serializers.PrimaryKeyRelatedField(source='user.last_name', read_only=True)
    class Meta:
        model = Client
        fields = [
            'id',
            'uuid',
            'user',
            'first_name',
            'last_name',
            'patronymic',
            'phone',
            'slug',
            'age',
            'sex',
            'training_level',
            'high',
            'weight',
            'wish_weight',
            'avatar',
            'is_banned',
            'is_member',
            'workout_profile_completed',
            'nutriment_profile_completed',
            'personal_workout_profile',
            'personal_nutriment_profile',
            'foodprogram_set',
            'favourite_set',
            'created',
            'updated',
        ]


class ClientRegenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'regenerate_food',
            ]


class ClientProgressSerializer(serializers.ModelSerializer):
    progress_set = ProgressSerializer(read_only=True, many=True)
    class Meta:
        model = Client
        fields = [
            'progress_set',
            ]


class ClientMessageSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Client
        fields = [
            'messages',
        ]

    def get_trainer(self, message):
        name = message.trainer.user.first_name
        last_name = message.trainer.user.last_name
        return '{0}{1}'.format(name, last_name)

    def get_client_id(self, message):
        if message.client:
            return message.client.id, True
        return None, False

    def get_messages(self, obj):
        leaduser = obj.leaduser
        boss_trainer = Trainer.objects.get(is_boss=True)
        trainer = obj.trainer

        if leaduser != None:
            leaduser_thread_qs = Thread.objects.filter(leaduser=leaduser, trainer=boss_trainer)
        else:
            leaduser_thread_qs = Thread.objects.none()

        leaduser_thread_obj = None
        if leaduser_thread_qs.exists():
            leaduser_thread_obj = leaduser_thread_qs[0]

        client_thread_qs = Thread.objects.filter(client=obj, trainer=trainer)
        client_thread_obj = None
        if client_thread_qs.exists():
            client_thread_obj = client_thread_qs[0]

        messages = ChatMessage.objects.filter(
            Q(thread=leaduser_thread_obj)|
            Q(thread=client_thread_obj)
            ).distinct().order_by('-timestamp')[:300]

        data = {}
        for message in messages:
            message_item = {}
            message_item['thread'] = message.thread.id
            message_item['trainer'] = self.get_trainer(message)
            message_item['client'] = self.get_client_id(message)[0]
            message_item['message'] = message.message
            message_item['userhandle'] = message.userhandle
            message_item['timestamp'] = message.timestamp
            data[message.id] = message_item
        return data


class ClientCreateSerializer(serializers.Serializer):
    workout_profile_completed = serializers.BooleanField(default=False)
    nutriment_profile_completed = serializers.BooleanField(default=False)
    uuid = serializers.CharField(required=True, max_length=25)
    leaduser_id = serializers.IntegerField()
    age = serializers.IntegerField()
    high = serializers.IntegerField()
    weight = serializers.FloatField(max_value=499, min_value=0)
    wish_weight = serializers.FloatField(max_value=499, min_value=0)
    avatar = serializers.ImageField(required=False)
    sex = serializers.ChoiceField(choices=SEX)
    training_level = serializers.ChoiceField(choices=LEVELS)
    promo = serializers.CharField(required=False, allow_blank=True, max_length=100)


def get_promo_obj(promo):
    try:
        promo_obj = Promo.objects.get(name=promo.lower())
    except:
        promo_obj = None
    return promo_obj

def instance_has_payed_orders(instance):
    return instance.order_set.filter(payed=True).count() > 0


class UserSerializer(serializers.ModelSerializer):
    client = ClientCreateSerializer(required=True)
    # username = serializers.CharField(validators=[validators.ValidationError(message='Введите правильное имя пользователя. Оно может содержать только буквы, цифры и знаки @/./+/-/_.')])
    class Meta:
        model = User
        fields = ('id', 'username','password', 'email','first_name', 'last_name', 'client',)
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        """
        Check that the start is before the stop.
        """
        search = re.sub(re.compile("[^A-Za-z0-9-_]+"), "", value)
        if search != value:
            raise serializers.ValidationError("Введите правильное имя пользователя. Оно может содержать только буквы, цифры и знаки -/_")
        return value

    def create(self, validated_data):
        client_data = validated_data.pop('client')

        ## CREATE USER OBJ
        user_obj = User.objects.create(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                username=validated_data['username'],
                password = make_password(validated_data['password'])
        )

        # # GET LEADUSER OBJ
        try:
            leaduser_obj = LeadUser.objects.get(id=client_data['leaduser_id'])
        except Exception as e:
            leaduser_obj = None

        ## MAKE PROMO RELATION
        promo = client_data.get('promo', None)
        promo_obj = get_promo_obj(promo)
        if promo != None:
            try:
                partner = Partner.objects.get(promocode=promo.lower())
                trainer_obj = partner.trainer
            except Exception as e:
                trainer_obj = Trainer.objects.get(user__username='sportapps_trainer')
        else:
            trainer_obj = Trainer.objects.get(user__username='sportapps_trainer')

        ## CREATE CLIENT
        try:
            instance = Client(
                leaduser = leaduser_obj,
                user = user_obj,
                uuid = client_data['uuid'],
                trainer = trainer_obj,
                age = client_data['age'],
                sex = client_data['sex'],
                training_level = client_data['training_level'],
                high = client_data['high'],
                weight = client_data['weight'],
                wish_weight = client_data['wish_weight'],
                slug = user_obj.username,
                avatar = client_data.get('avatar', 'accounts/noavatar.png'),
                workout_profile_completed = client_data['workout_profile_completed'],
                nutriment_profile_completed = client_data['nutriment_profile_completed'],
                ref_promo = promo,
                )

            try:
                instance.clean()
            except Exception as e:
                raise serializers.ValidationError(e.args[0])
            instance.save()

            personal_workout_profile_obj = PersonalWorkoutProfile.objects.create(
                client=instance,
                )
            personal_nutriment_profile_obj = PersonalNutrimentProfile.objects.create(
                client=instance,
                )

            client_group = Group.objects.get(name='clients')
            client_group.user_set.add(user_obj)

            ## CHECK IF PROMO IS FREE & MAKE CLIENT ORDER
            if promo_obj != None:
                if promo_obj.free:
                    if not promo_obj.used:
                        days = promo_obj.catalog_order_time.days
                        amount = 0
                        order_obj = Order.objects.create(client=instance, catalog=True, catalog_order_time=days, amount=amount, payed=True)

                        # SAVE  CLIENT AS A MEMBER
                        instance.is_member = True

                        #CHECK IF PROMO_OBJ HAS PARTNER WITH TRAINER
                        try:
                            trainer_obj = promo_obj.partner.trainer
                            if trainer_obj:
                                instance.trainer = trainer_obj
                        except Exception as e:
                            pass

                        instance.save()

                        # SAVE FREE PROMO OBJECT AS USED
                        promo_obj.used = True
                        promo_obj.save()

        except Exception as e:
            raise serializers.ValidationError(e)

        # MAKE 7 DAYS TRIAL
        if not instance_has_payed_orders(instance):
            order_obj = Order.objects.create(client=instance, payed=True, catalog=True, catalog_order_time=7, trial=True)


        return user_obj












