# -*- coding: utf-8 -*-
from rest_framework.reverse import reverse as api_reverse
from rest_framework import routers, serializers
from options.models import (
    Muscle,
    Exercise,
    Competition,
    Product,
    Recipe,
    FitnessClub,
    FitnessClubImage,
    Exercise,
    Kbzu100g,
    Kbzu1Portion,
    )


class MuscleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api-options:muscle_detail',
        lookup_field='pk',
        )
    class Meta:
        model = Muscle
        fields = [
            'id',
            'url',
            'name',
            'created',
            'updated',
        ]


class Kbzu1PortionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kbzu1Portion
        fields = [
            'id',
            'weight',
            'protein',
            'fat',
            'carbohydrate',
            'kkal',
            'created',
            'updated',
        ]


class Kbzu100gPortionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kbzu100g
        fields = [
            'id',
            'weight',
            'protein',
            'fat',
            'carbohydrate',
            'kkal',
            'created',
            'updated',
        ]

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'portion_number',
            'recipe_type',
            'recipe_appointment',
            'recipe_food_type',
            'recipe_mode',
            'recipe_time',
            'recipe_method',
            'ingridients',
            'instructions',
            'created',
            'updated',
        ]

class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api-options:product_detail',
        lookup_field='pk',
        )
    recipe = RecipeSerializer(read_only=True)
    kbzu_1portion = Kbzu1PortionSerializer(read_only=True)
    class Meta:
        model = Product
        fields = [
            'id',
            'url',
            'name',
            'recipe',
            'kbzu_1portion',
            'created',
            'updated',
        ]


class FitnessClubImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessClubImage
        fields = [
            'id',
            'fitnessclub',
            'image',
            'created',
            'updated',
        ]


class FitnessClubSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api-options:fitnessclub_detail',
        lookup_field='pk',
        )
    fitnessclubimage_set = FitnessClubImageSerializer(read_only=True, many=True)
    class Meta:
        model = FitnessClub
        fields = [
            'id',
            'url',
            'name',
            'content',
            'video_url',
            'fitnessclubimage_set',
            'created',
            'updated',
        ]


class CompetitionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api-options:competition_detail',
        lookup_field='pk',
        )
    class Meta:
        model = Competition
        fields = [
            'id',
            'url',
            'content',
            'name',
            'image',
            'video',
            'start_date',
            'finish_date',
            'status',
            'created',
            'updated',
        ]


class ExerciseSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api-options:exercise_detail',
        lookup_field='pk',
        )
    muscles = MuscleSerializer(read_only=True, many=True)
    other_muscles = MuscleSerializer(read_only=True, many=True)
    class Meta:
        model = Exercise
        fields = [
            'id',
            'url',
            'name',
            'muscles',
            'other_muscles',
            'content',
            'video',
            'short_video',
            'created',
            'updated',
        ]



