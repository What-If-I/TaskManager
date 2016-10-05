from django.views import generic

from .models import Task
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import translation


class IndexView(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    template_name = 'task_manager/index.html'
    context_object_name = 'tasks_by_days'

    user_language = 'en-us'
    translation.activate(user_language)

    def get_queryset(self):
        """return tasks of logged in user"""
        return Task.count_by_date(owner=self.request.user.id)


class DetailView(LoginRequiredMixin, generic.DetailView):
    login_url = '/login/'
    model = Task
    context_object_name = 'user_task'
    template_name = 'task_manager/detail.html'

    def get_queryset(self):
        return Task.get_all_user_tasks_from_today(self.request.user.id)
