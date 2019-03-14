# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import permissions
from sportapps.restconf.permissions import ClientPermissionOnly, LeadPermissionOnly

from options.models import Muscle, Competition, Product, FitnessClub, FitnessClubImage, Exercise
from rest_framework import generics, mixins
from options.api.serializers import MuscleSerializer, ProductSerializer, FitnessClubSerializer, FitnessClubImageSerializer, CompetitionSerializer, ExerciseSerializer


class MuscleListAPIView(generics.ListAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Muscle.objects.all()
    serializer_class = MuscleSerializer


class MuscleRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Muscle.objects.all()
    serializer_class = MuscleSerializer


class ProductListAPIView(generics.ListAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class FitnessClubListAPIView(generics.ListAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = FitnessClub.objects.all()
    serializer_class = FitnessClubSerializer


class FitnessClubRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = FitnessClub.objects.all()
    serializer_class = FitnessClubSerializer


class FitnessClubImageRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = FitnessClubImage.objects.all()
    serializer_class = FitnessClubImageSerializer

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class CompetitionListAPIView(generics.ListAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer


class CompetitionRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

class ExerciseListAPIView(generics.ListAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer


class ExerciseRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, ClientPermissionOnly]
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer



