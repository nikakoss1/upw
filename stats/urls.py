from django.conf.urls import  url
from stats.views import DailyStatListView, DownloadRefererListView

urlpatterns = [
    url(r'^daily-stat/$', DailyStatListView.as_view(), name="daily_stat_list"),
    url(r'^download-referers/$', DownloadRefererListView.as_view(), name="download_referer_list"),

]
