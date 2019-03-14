# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .serializers import AppsettingsSerializer
from rest_framework import generics, mixins
from appsettings.models import AppSettings
from sportapps.restconf.permissions import ClientPermissionOnly, LeadPermissionOnly


class AppsettingsRetriveView(generics.RetrieveAPIView):
    permission_classes = [LeadPermissionOnly]
    queryset = AppSettings.objects.all()
    serializer_class = AppsettingsSerializer
    lookup_field = 'pk'



