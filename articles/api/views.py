# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import permissions
from sportapps.restconf.permissions import (
    ClientPermissionOnly,
    LeadPermissionOnly,
    IsOwnerOrReadOnly,
    UserPermissionOnly,
    PublisherPermissionOnly,
    )

from articles.models import (
    Article,
    ArticleImage,
    Like,
    Comment,
    )
from rest_framework import generics, mixins
from articles.api.serializers import (
    ArticleCreateSerializer,
    ArticleSerializer,
    ArticleImageSerializer,
    LikeSerializer,
    CommentSerializer,
    )
from accounts.models import (
    Trainer,
    Client,
    )

def get_user_ids(trainer):
    user_ids = []
    clients = Client.objects.filter(trainer=trainer)
    for client in clients:
        user_ids.append(client.user.id)
    return user_ids



class ArticleListAPIView(generics.ListAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

    # def get_queryset(self):
    ##### DIFFERENT POSTS FROM EACH OWN TRAINER
    # try:
    #     trainer = self.request.user.client.trainer
    #     trainer_users = get_user_ids(trainer)
    #     qs_trainer = Article.objects.filter(draft=False, user__trainer=trainer)
    #     qs_users = Article.objects.filter(draft=False, user__id__in=trainer_users)
    #     return qs_trainer|qs_users
    # except Exception as e:
    #     trainer = Trainer.objects.get(is_boss=True)
    #     trainer_users = get_user_ids(trainer)
    #     qs_trainer = Article.objects.filter(draft=False, user__trainer=trainer)
    #     qs_users = Article.objects.filter(draft=False, user__id__in=trainer_users)
    #     return qs_trainer|qs_users


    # def get_serializer_context(self, *args, **kwargs):
    #     return {"request": self.request}


class ArticleCreateAPIView(generics.CreateAPIView):
    permission_classes = [LeadPermissionOnly,]
    queryset = Article.objects.all()
    serializer_class = ArticleCreateSerializer
    lookup_field = 'slug'


class ArticleRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'


class ArticleUpdateAPIView(mixins.DestroyModelMixin,  mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly, IsOwnerOrReadOnly]
    queryset = Article.objects.all()
    serializer_class = ArticleCreateSerializer
    lookup_field = 'slug'


    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ArticleImageCreateAPIView(generics.CreateAPIView):
    permission_classes = [LeadPermissionOnly,]
    queryset = ArticleImage.objects.all()
    serializer_class = ArticleImageSerializer


class ArticleImageRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = ArticleImage.objects.all()
    serializer_class = ArticleImageSerializer


class ArticleImageUpdateAPIView(mixins.DestroyModelMixin,  mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = ArticleImage.objects.all()
    serializer_class = ArticleImageSerializer
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class LikeCreateAPIView(generics.CreateAPIView):
    permission_classes = [LeadPermissionOnly, UserPermissionOnly]
    queryset = Like.objects.all()
    serializer_class = LikeSerializer


class CommentCreateAPIView(generics.CreateAPIView):
    permission_classes = [LeadPermissionOnly, PublisherPermissionOnly]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer






