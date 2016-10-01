import collections

from django.shortcuts import render
from django.views import generic
from django.db.models import Count

from .models import Task


class IndexView(generic.ListView):
    template_name = 'task_manager/index.html'
    context_object_name = 'user_tasks'

    def get_queryset(self):
        """return tasks of logged in user"""
        tasks_query = Task.get_all_user_tasks_from_today(self.request.user.id).values().order_by('due_to_date')
        tasks_dict = collections.defaultdict(list)
        dict_list = []
        for tasks_dictionary in tasks_query:
            dict_list.append(tasks_dictionary)
            for task_dict in dict_list:
                tasks_dict[task_dict['due_to_date']].append(task_dict)
        dicts_dict = {k: v for k, v in tasks_dict.items()}
        return dicts_dict


class DetailView(generic.DetailView):
    model = Task
    context_object_name = 'user_task'
    template_name = 'task_manager/detail.html'

    def get_queryset(self):
        return Task.get_all_user_tasks_from_today(self.request.user.id)
