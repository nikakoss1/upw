from accounts.models import Client
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from preferences import preferences
from subscriptions.models import (
    Program,
    )
from options.models import Exercise
# from rest_framework_jwt.views import verify_jwt_token
from rest_framework_jwt.serializers import VerificationBaseSerializer
from rest_framework_jwt.settings import api_settings

# User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

def has_group(user, group):
    return user.groups.filter(name=group).exists()

def has_multiple_group(user, groups):
    return user.groups.filter(name__in=groups).exists()

class IsContentOwnerMixin(object):
    def is_content_owner(self, obj):
        user = self.request.user
        content_owner = obj.content_owner.user
        if user != content_owner:
            raise Http404
        return

class IsYourTrainerPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            trainer = self.request.user.trainer
            obj = self.get_object()
            if not obj in trainer.trainer_set.all():
                raise Http404
            return super(IsYourTrainerPermissionMixin, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            raise Http404


class TokenIsVerified(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.token = self.request.GET['token']
            payload = jwt_decode_handler(self.token)
            username = jwt_get_username_from_payload(payload)
            user = User.objects.get_by_natural_key(username)
            if not user.client:
                redirect('/lg')
            self.client = user.client
        except:
            return redirect('/lg')
        return super(TokenIsVerified, self).dispatch(request, *args, **kwargs)


class IsYourClientPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            user = request.user
            if not has_group(user, 'brandowners'):
                trainer = user.trainer
                help_trainers = trainer.trainer_set.all()
                obj = self.get_object()
                clients = Client.objects.filter(
                    Q(trainer=trainer)|
                    Q(trainer__in=help_trainers)
                    )
                if not obj in clients:
                    raise Http404
            return super(IsYourClientPermissionMixin, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            raise Http404


class HasGroupPermissionMixin(object):
    def has_multiple_group(self, *groups):
        user = self.request.user
        if not user.groups.filter(name__in=groups).exists():
            raise Http404
        return


class SeoMixin(models.Model):
    seo_title = models.CharField('СЕО тайтл', max_length=120, blank=True)
    seo_desc = models.TextField('МЕТА описание', blank=True)
    keywords = models.CharField('СЕО киворды', max_length=120, blank=True)

    class Meta:
        abstract = True

class ComingSoonMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if preferences.AppSettings.coming_soon:
            return redirect('coming_soon')
        return super(ComingSoonMixin, self).dispatch(request, *args, **kwargs)

class LoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise Http404
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

class NotSuperuserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if  request.user.is_superuser:
            raise Http404
        return super(NotSuperuserMixin, self).dispatch(request, *args, **kwargs)

class AdministrationPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            group = 'administration'
            user = request.user
            if not has_group(user, group):
                raise Http404
        return super(AdministrationPermissionMixin, self).dispatch(request, *args, **kwargs)

class TrainersPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            group = 'trainers'
            user = request.user
            if not has_group(user, group):
                raise Http404
        return super(TrainersPermissionMixin, self).dispatch(request, *args, **kwargs)


class ClientListOfTrainerPermissionMixin(MultipleObjectMixin):

    def get_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset' or 'model'" % self.__class__.__name__)

        try:
            user = self.request.user
            if has_group(user, 'brandowners'):
                return queryset
            elif has_group(user, 'trainers'):
                queryset = queryset.filter(trainer=user.trainer)
            else:
                queryset = queryset.none()
        except Exception as e:
            if not self.request.user.is_superuser:
                queryset = queryset.none()
            pass
        return queryset



## DELETE
class ClientOwnerPermissionMixin(SingleObjectMixin):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not has_group(user, 'brandowners'):
            try:
                slug = self.kwargs['slug']
                client = Client.objects.get(slug=slug)
                if client.trainer != request.user.trainer:
                    redirect(reverse_lazy('accounts:client_list'))
            except Exception as e:
                raise Http404
        return super(ClientOwnerPermissionMixin, self).dispatch(request, *args, **kwargs)


class BrandOwnersPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            group = 'brandowners'
            user = request.user
            if not has_group(user, group):
                raise Http404
        return super(BrandOwnersPermissionMixin, self).dispatch(request, *args, **kwargs)

## LEAD USERS (!!! CHANGE FOR REAL DATA IN PRODUCTION !!!)
class LeadUserPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                # if not request.GET('key', False):
                #     raise Http404
                # elif not request.GET('uuid', False):
                #     raise Http404
                pass
            except Exception as e:
                raise Http404
        return super(LeadUserPermissionMixin, self).dispatch(request, *args, **kwargs)


class BrandOwnersContentManagersPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            groups = ['brandowners', 'contentmanagers']
            user = request.user
            if not has_multiple_group(user, groups):
                raise Http404
        return super(BrandOwnersContentManagersPermissionMixin, self).dispatch(request, *args, **kwargs)


class TrainersContentManagersPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            groups = ['trainers', 'contentmanagers']
            user = request.user
            if not has_multiple_group(user, groups):
                raise Http404
        return super(TrainersContentManagersPermissionMixin, self).dispatch(request, *args, **kwargs)

class IsAuthenticatedPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise Http404
        return super(IsAuthenticatedPermissionMixin, self).dispatch(request, *args, **kwargs)

class IsClientPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            client = self.request.user.client
            return super(IsClientPermissionMixin, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            raise Http404


class PersonalWorkoutProgramExist(object):
    def dispatch(self, request, *args, **kwargs):
        if not Program.objects.filter(program_type='WP').first():
            raise Http404
        return super(PersonalWorkoutProgramExist, self).dispatch(request, *args, **kwargs)


class PersonalFoodProgramExist(object):
    def dispatch(self, request, *args, **kwargs):
        if not Program.objects.filter(program_type='FP').first():
            raise Http404
        return super(PersonalFoodProgramExist, self).dispatch(request, *args, **kwargs)


class IsmemberPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            is_member = self.request.user.client.is_member
            return super(IsClientPermissionMixin, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            raise Http404

class PayProgramPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            if obj.chargeable == True:
                if request.user.client.is_member:
                    return super(PayProgramPermissionMixin, self).dispatch(request, *args, **kwargs)
                else:
                    raise Http404
            else:
                return super(PayProgramPermissionMixin, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            raise Http404

class ContentOwnerPermissionMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            trainer = request.user.trainer
            if trainer.is_boss:
                return super(ContentOwnerPermissionMixin, self).dispatch(request, *args, **kwargs)
            qs = Exercise.objects.filter(content_owner=trainer)
            exercise = self.get_object()
            if exercise in qs:
                return super(ContentOwnerPermissionMixin, self).dispatch(request, *args, **kwargs)
            return redirect(reverse_lazy('options:exercise_list'))
        except Exception as e:
            return redirect(reverse_lazy('options:exercise_list'))

def get_client(self):
    slug = self.kwargs['slug']
    client_obj = Client.objects.get(slug=slug)
    return client_obj

class WorkoutCounterPositive(object):
    def dispatch(self, request, *args, **kwargs):
        client_obj = get_client(self)
        personal_workout_profile = client_obj.personalworkoutprofile
        if personal_workout_profile.workout_counter <= 0:
            raise Http404
        return super(WorkoutCounterPositive, self).dispatch(request, *args, **kwargs)


class NutrimentCounterPositive(object):
    def dispatch(self, request, *args, **kwargs):
        client_obj = get_client(self)
        personal_nutriment_profile = client_obj.personalnutrimentprofile
        if personal_nutriment_profile.nutriment_counter <= 0:
            raise Http404
        return super(NutrimentCounterPositive, self).dispatch(request, *args, **kwargs)


