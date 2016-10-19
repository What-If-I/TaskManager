from django.conf.urls import url
from . import views

app_name = 'task_manager'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.TaskView.as_view(), name='detail'),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[-\w]+)/(?P<day>[0-9]+)/$', views.DailyTaskView.as_view(), name="date_tasks"),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[-\w]+)/(?P<day>[0-9]+)/(?P<pk>[0-9]+)/$',
        views.TaskView.as_view(), name="task"),
    ]
