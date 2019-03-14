# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from accounts.api.serializers import (
    BossTrainerSerializer,
    CategorySerializer,
    ClientMessageSerializer,
    ClientProgressSerializer,
    ClientSerializer,
    ClientShortSerializer,
    ExerciseCommentSerializer,
    FavouriteSerializer,
    FoodProgramSerializer,
    LeadUserMessageSerializer,
    LeadUserSerializer,
    LeadUserNewMessagesSerializer,
    ClientNewMessagesSerializer,
    PersonalNutrimentProfileSerializer,
    PersonalWorkoutProfileSerializer,
    ProgramSerializer,
    ProgressSerializer,
    UserSerializer,
    WorkoutCommentSerializer,
    WorkoutSerializer,
    ClientRegenerateSerializer,
    ClientFoodProgramUpdateSerializer,
    )
from accounts.models import (
    Client,
    Day,
    ExerciseComment,
    Food,
    FoodProgram,
    LeadUser,
    Message,
    PersonalNutrimentProfile,
    PersonalWorkoutProfile,
    PORTIONS,
    Progress,
    Time,
    Trainer,
    Workout,
    WorkoutComment,
    )
from appsettings.utils import *
from chat.models import Thread, ChatMessage
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.utils import timezone
from rest_framework import generics, mixins
from rest_framework import permissions
from rest_framework.views import APIView
from sportapps.restconf.permissions import (
    ClientPermissionOnly,
    LeadPermissionOnly,
    IsOwnerOrReadOnly
    )
from subscriptions.models import (
    Category,
    Program,
    Favourite,
    )
import datetime
from datetime import timedelta
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status, viewsets
from subscriptions.daily_workout_generator import daily_workout_generator
today = datetime.date.today()


########################################################################################################################
## LEADUSERS
class LeadUserCreateAPIView(generics.CreateAPIView):
    queryset = LeadUser.objects.all()
    serializer_class = LeadUserSerializer

class LeadUserRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = LeadUser.objects.all()
    serializer_class = LeadUserSerializer
    lookup_field = 'pk'

class LeadUserMessagesAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = LeadUser.objects.all()
    serializer_class = LeadUserMessageSerializer
    lookup_field = 'pk'


########################################################################################################################
## CHAT

class LeadUserMessageStatusUpdateAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = LeadUser.objects.all()
    serializer_class = LeadUserNewMessagesSerializer
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class ClientMessageStatusUpdateAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Client.objects.all()
    serializer_class = ClientNewMessagesSerializer
    lookup_field = 'slug'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


########################################################################################################################
## TRAINERS

class BossTrainerRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Trainer.objects.all()
    serializer_class = BossTrainerSerializer
    lookup_field = 'pk'

    def get_object(self):
        try:
            trainer = self.request.user.client.trainer
            if has_group(trainer.user, 'trainers'):
                trainer = trainer.main_trainer
        except:
            queryset = self.get_queryset()
            filter = {'is_boss':True}
            trainer = get_object_or_404(queryset, **filter)
            self.check_object_permissions(self.request, trainer)
        return trainer

########################################################################################################################
## CLIENTS

class WorkoutCommentCreateAPIView(generics.CreateAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = WorkoutComment.objects.all()
    serializer_class = WorkoutCommentSerializer

class RegenerateFood(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    # permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Client.objects.all()
    serializer_class = ClientRegenerateSerializer
    lookup_field = 'slug'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ClientRetrieveAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'slug'


class ClientShortRetrieveAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Client.objects.all()
    serializer_class = ClientShortSerializer
    lookup_field = 'slug'


class ClientProgressRetrieveAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Client.objects.all()
    serializer_class = ClientProgressSerializer
    lookup_field = 'slug'


class ClientCreateAPIView(APIView):
    permission_classes = [LeadPermissionOnly]
    serializer_class = UserSerializer

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientMessagesAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ]
    queryset = Client.objects.all()
    serializer_class = ClientMessageSerializer
    lookup_field = 'slug'


class ClientFoodProgramUpdateAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ]
    queryset = Client.objects.all()
    serializer_class = ClientFoodProgramUpdateSerializer
    lookup_field = 'slug'
    params = {
        'Программа питания для похудения':0.7,
        'Здоровое питание':1,
        'Программа питания для набора массы':1.2,
    }

    def get_kf(self, program_name):
        return self.params[program_name]

    def create_foodprogram(self, foodprogram, target_client):
        return FoodProgram.objects.create(
                client=target_client,
                program=foodprogram.program,
                leaduser=foodprogram.leaduser,
                number=foodprogram.number,
                name=foodprogram.name,
                content=foodprogram.content,
            )

    def create_day(self, day, new_foodprogram):
        return Day.objects.create(
                foodprogram=new_foodprogram,
                name=day.name,
                sorting=day.sorting,
                day_kbzu=day.day_kbzu,
            )

    def create_time(self, time, new_day):
        return Time.objects.create(
                number=time.number,
                settingstime=time.settingstime,
                day=new_day,
            )

    def get_change_kf(self, target_kkal, src_kkal):
        return target_kkal / src_kkal

    def get_kbzu(self, food, target_kkal, src_kkal):
        change_kf = self.get_change_kf(target_kkal, src_kkal)
        weight = food.weight * change_kf
        kkal = food.kkal * change_kf
        protein = food.protein * change_kf
        fat = food.fat * change_kf
        carbohydrate = food.carbohydrate * change_kf
        return weight, kkal, protein, fat, carbohydrate

    def create_food(self, new_foodprogram, new_day, new_time, food, target_kkal, src_kkal):
        weight, kkal, protein, fat, carbohydrate = self.get_kbzu(food, target_kkal, src_kkal)
        return Food.objects.create(
                    foodprogram=new_foodprogram,
                    day=new_day,
                    time=new_time,
                    product=food.product,
                    weight=weight,
                    kkal=kkal,
                    protein=protein,
                    fat=fat,
                    carbohydrate=carbohydrate,
                )

    def foodprograms_delete(self, current_foodprograms):
        return FoodProgram.objects.filter(id__in=current_foodprograms).delete()

    def generate_similar_foodprogram(self, src_client, target_client):

        lst = []
        ## GET ALL FOODPROGRAMS OF THE SRC_CLIENT
        src_foodprograms = src_client.foodprogram_set.all()
        current_foodprograms = list(target_client.foodprogram_set.values_list('id',flat=True))
        if src_foodprograms.count() == 0:
            return

        try:
            for foodprogram in src_foodprograms:
                new_foodprogram = self.create_foodprogram(foodprogram, target_client)

                for day in foodprogram.day_set.all():
                    new_day = self.create_day(day, new_foodprogram)

                    for time in day.time_set.all():
                        new_time = self.create_time(time, new_day)

                        for food in reversed(time.food_set.all()):
                            kf = self.get_kf(foodprogram.program.name)
                            target_kkal = target_client.dk * kf
                            src_kkal = src_client.dk * kf
                            new_food = self.create_food(new_foodprogram, new_day, new_time, food, target_kkal, src_kkal)

        except Exception as e:
            print(e)

        ## DELETE CURRENT FOODPROGRAMS
        self.foodprograms_delete(current_foodprograms)

        return

    def put(self, request, *args, **kwargs):
        try:
            src_client = Client.objects.get(slug=request.data['src_login'])
            target_client = self.get_object()
            self.generate_similar_foodprogram(src_client, target_client)
        except Exception as e:
            print(e)
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

########################################################################################################################
## PROGRESS

class ProgressCreateAPIView(generics.CreateAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer


class ProgressRetrieveAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

########################################################################################################################
## PERSONAL WORKOUT PROFILE

class PersonalWorkoutProfileRetrieveAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = PersonalWorkoutProfile.objects.all()
    serializer_class = PersonalWorkoutProfileSerializer
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

########################################################################################################################
## PERSONAL NUTRIMENT PROFILE

class PersonalNutrimentProfileRetrieveAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = PersonalNutrimentProfile.objects.all()
    serializer_class = PersonalNutrimentProfileSerializer
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


########################################################################################################################
## WORKOUT COMMENTS

class ExerciseCommentCreateAPIView(generics.CreateAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = ExerciseComment.objects.all()
    serializer_class = ExerciseCommentSerializer

class ExerciseCommentRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = ExerciseComment.objects.all()
    serializer_class = ExerciseCommentSerializer
    lookup_field = 'pk'


########################################################################################################################
## WORKOUTS

class WorkoutRetrieveAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):
        workout_obj = Workout.objects.get(pk=kwargs['pk'])
        if request.data.get('start', False):
            if workout_obj.start == False:
                workout_obj.start_date = datetime.datetime.now()
                workout_obj.save()
                workout_obj.activity(content='Старт тренировки {}'.format(workout_obj.start_date))
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


########################################################################################################################
## FOODPROGRAMS

class FoodProgramRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = FoodProgram.objects.all()
    serializer_class = FoodProgramSerializer
    lookup_field = 'pk'


class MarafonProgramListAPIView(generics.ListAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer

    def get_queryset(self):
        return Program.objects.filter(
            program_type='MT',
            ).filter(is_active=True)


class FavouriteCreateAPIView(generics.CreateAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer

class FavouriteDeleteAPIView(APIView):
    """
    Retrieve, update or delete a favourite instance.
    """
    def get_object(self, pk):
        try:
            return Favourite.objects.get(pk=pk)
        except Favourite.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        favourite_obj = self.get_object(pk)
        serializer = FavouriteSerializer(favourite_obj)
        return Response(serializer.data)


    def delete(self, request, pk, format=None):
        favourite_obj = self.get_object(pk)
        favourite_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProgramListAPIView(generics.ListAPIView):
    permission_classes = [LeadPermissionOnly,]
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer

    def get_queryset(self):
        return Program.objects.filter(is_active=True)

class ProgramCategoryListAPIView(generics.ListAPIView):
    permission_classes = [LeadPermissionOnly,]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(program__is_active=True).distinct()

class ProgramByCategoryListAPIView(generics.ListAPIView):
    permission_classes = [LeadPermissionOnly,]
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    serializer_class_category = CategorySerializer

    def get_serializer_class(self, ):
        category_id = self.kwargs['pk']
        program_category = Category.objects.get(id=category_id)
        if program_category.category_set.filter().exists():
            return self.serializer_class_category
        return super(ProgramByCategoryListAPIView, self).get_serializer_class()

    def get_queryset(self):
        category_id = self.kwargs['pk']
        program_category = Category.objects.get(id=category_id)
        if program_category.category_set.filter().exists():
            return program_category.category_set.filter(program__is_active=True).distinct()
        return Program.objects.filter(category=program_category)


def has_generated_workouts(obj):
    return obj.workout_set.filter(date=today).count() > 0

class ProgramRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    lookup_field = 'pk'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        if obj.daily:
            if not has_generated_workouts(obj):
                daily_workout_generator(obj, 90)
                return obj
        return obj




