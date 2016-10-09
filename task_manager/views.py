from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views import generic

from .models import Task, TaskForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect


class IndexView(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    template_name = 'task_manager/index.html'
    context_object_name = 'tasks_by_days'

    def get_queryset(self):
        """return tasks of logged in user"""
        return Task.user_tasks_count_by_date(owner=self.request.user.id)

    def post(self, request, *args, **kwargs):
        reminder = self.request.POST['notification-time']

        task_form = TaskForm(
            {
                'title': self.request.POST['title'],
                'description': self.request.POST['description'],
                'due_to_date': self.request.POST['complete-date'],
                'reminder': reminder.replace("T", " "),  # remove 'T' before time
            }
        )
        if task_form.is_valid():
            Task(owner=self.request.user, **task_form.cleaned_data).save()
            return redirect(reverse('task_manager:index'))

        else:
            print(task_form.errors)
            return render(self.request, self.template_name,
                          context={
                              'tasks_by_days': self.get_queryset(),
                              'open_task_form': True,
                              'task_form': task_form,
                              'task_form_reminder': reminder,
                          })


class DetailView(LoginRequiredMixin, generic.DetailView):
    login_url = '/login/'
    model = Task
    context_object_name = 'user_task'
    template_name = 'task_manager/detail.html'

    def get_queryset(self):
        return Task.get_all_user_tasks_from_today(self.request.user.id)
