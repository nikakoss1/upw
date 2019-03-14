from django.conf.urls import  url
from .views import (
        PartnerCreateView,
        PartnerUpdateView,
        PartnerDetailView,
        PartnerDeleteView,
        PartnerListView,
        PromoCreateView,
        PromoUpdateView,
        PromoDeleteView,
        PromoListView,
        ProgramPaySuccessRedirectView,
        )

urlpatterns = [
    # PARTNERS
    url(r'^$', PartnerListView.as_view(), name="partner_list"),
    url(r'^(?P<pk>\d+)/detail/$', PartnerDetailView.as_view(), name="partner_detail"),
    url(r'^(?P<pk>\d+)/promo-generate/$', ProgramPaySuccessRedirectView.as_view(), name="promo_generate"),
    url(r'^(?P<pk>\d+)/update/$', PartnerUpdateView.as_view(), name="partner_update"),
    url(r'^(?P<pk>\d+)/delete/$', PartnerDeleteView.as_view(), name="partner_delete"),
    url(r'^add/$', PartnerCreateView.as_view(), name="partner_create"),

    # PROMOCODES
    url(r'^promo/$', PromoListView.as_view(), name="promo_list"),
    url(r'^promo/(?P<pk>\d+)/update/$', PromoUpdateView.as_view(), name="promo_update"),
    url(r'^promo/(?P<pk>\d+)/delete/$', PromoDeleteView.as_view(), name="promo_delete"),
    url(r'^promo/add/$', PromoCreateView.as_view(), name="promo_create"),
]

