from django.urls.base import reverse
from django.shortcuts import render
from django.views import generic
from .models import Task, TaskForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class IndexView(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    template_name = 'task_manager/index.html'
    context_object_name = 'tasks_by_days'

    def get_queryset(self):
        """return tasks of logged in user"""
        return Task.user_tasks_count_by_date(owner=self.request.user.id)

    def post(self, request, *args, **kwargs):
        """Submit new task"""
        reminder = self.request.POST['notification-time']

        task_form = TaskForm(
            {
                'title': self.request.POST['title'],
                'description': self.request.POST['description'],
                'due_to_date': self.request.POST['complete-date'],
                'reminder': reminder.replace("T", " "),  # remove 'T' between date and time
            }
        )
        if task_form.is_valid():
            Task(owner=self.request.user, **task_form.cleaned_data).save()
            return redirect(reverse('task_manager:index'))

        else:
            return render(self.request, 'task_manager/index.html',
                          context={
                              'tasks_by_days': self.get_queryset(),
                              'open_task_form': True,
                              'task_form': task_form,
                              'task_form_reminder': reminder,
                          })


class TaskView(LoginRequiredMixin, generic.DetailView):
    login_url = '/login/'
    model = Task
    context_object_name = 'user_task'
    template_name = 'task_manager/detail.html'
    allow_empty = False

    def get_queryset(self):
        return Task.get_all_user_tasks_from_today(self.request.user.id)


class DailyTaskView(LoginRequiredMixin, generic.DayArchiveView):
    login_url = '/login/'
    template_name = 'task_manager/by_day.html'
    context_object_name = 'day_tasks'
    date_field = "due_to_date"
    allow_future = True
    queryset = Task.objects.all()
    allow_empty = True

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner=self.request.user.id)

    def post(self, request, *args, **kwargs):
        """Submit new task"""
        reminder = self.request.POST['notificationTime']

        task_form = TaskForm(
            {
                'title': self.request.POST['title'],
                'description': self.request.POST['description'],
                'due_to_date': self.request.POST['completeDate'],
                'reminder': reminder.replace("T", " "),  # remove 'T' between date and time
            }
        )
        if task_form.is_valid():
            Task(owner=self.request.user, **task_form.cleaned_data).save()
            return redirect(self.request.path)

        else:
            return render(self.request, 'task_manager/by_day.html',
                          context={
                              'tasks_by_days': self.get_queryset(),
                              'open_task_form': True,
                              'task_form': task_form,
                              'task_form_reminder': reminder,
                          })