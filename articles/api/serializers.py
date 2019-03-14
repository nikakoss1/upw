# -*- coding: utf-8 -*-
from rest_framework.reverse import reverse as api_reverse
from rest_framework import routers, serializers
from articles.models import Article, ArticleImage, Like, Comment
from accounts.models import Trainer, Client
from django.utils.six.moves.urllib.parse import urlsplit

class ArticleCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = [
            'id',
            'user',
            'title',
            'content',
            'draft',
            'created',
            'updated',
        ]


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = [
            'id',
            'article',
            'user',
            'created',
            'updated',
        ]


class CommentSerializer(serializers.ModelSerializer):
    first_name = serializers.PrimaryKeyRelatedField(source='user.first_name', read_only=True)
    last_name = serializers.PrimaryKeyRelatedField(source='user.last_name', read_only=True)
    class Meta:
        model = Comment
        fields = [
            'id',
            'article',
            'user',
            'first_name',
            'last_name',
            'content',
            'created',
            'updated',
        ]


class ArticleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api-articles:article_detail_api',
        lookup_field='slug',
        )
    images = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    content = serializers.SerializerMethodField(read_only=True)
    like_number = serializers.SerializerMethodField(read_only=True)
    already_liked = serializers.SerializerMethodField(read_only=True)
    comment_set  =CommentSerializer(read_only=True, many=True)
    class Meta:
        model = Article
        fields = [
            'id',
            'url',
            'user',
            'title',
            'content',
            'draft',
            'images',
            'like_number',
            'already_liked',
            'comment_set',
            'created',
            'updated',
        ]

    def get_uri(self, image):
        request = self.context.get('request')
        return api_reverse("api-articles:articleimage_detail_api",  request=request)

    def get_images(self, obj):
        qs = obj.articleimage_set.all()
        data = {}
        for image in qs:
            data[image.id] = str(image.image)
        return data

    def get_scheme(self, request):
        return urlsplit(request.build_absolute_uri(None)).scheme

    def get_user(self, obj):
        request = self.context.get('request')
        scheme = self.get_scheme(request)
        host = request.META['HTTP_HOST']
        try:
            avatar = obj.user.client.avatar.url
        except Exception:
            avatar = obj.user.trainer.avatar.url
        except:
            avatar = 'accounts/noavatar.png'
        avatar = '{0}://{1}{2}'.format(scheme, host, avatar)
        data = {
        'id':obj.user.id,
        'first_name':obj.user.first_name,
        'last_name':obj.user.last_name,
        'avatar':avatar
        }
        return data

    def get_content(self, obj):
        request = self.context.get('request')
        return obj.content.replace('/media/', request.get_host() + '/media/')

    def get_like_number(self, obj):
        return str(obj.like_set.all().count())

    def get_already_liked(self, obj):
        request = self.context.get('request')
        try:
            if obj.like_set.filter(user=request.user).first():
                return True
            else:
                return False
        except:
            return False


class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = [
            'id',
            'article',
            'image',
            'created',
            'updated',
        ]




