import datetime

from collections import defaultdict
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django import forms


# todo: reminder can't be higher than due_to_date
class Task(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Owner')
    title = models.CharField(max_length=100, verbose_name='Task')
    due_to_date = models.DateField(default=datetime.date.today(), verbose_name='Due to')
    description = models.TextField('Description')
    reminder = models.DateTimeField('Reminder', blank=True, null=True)
    attached_file = models.FileField(upload_to='uploads/', blank=True, null=True, verbose_name='Document')
    is_done = models.BooleanField(default=False, verbose_name='Done')

    def not_from_past(self):
        today = datetime.date.today()
        return self.due_to_date >= today

    @classmethod
    def _get_future_tasks(cls):
        today = datetime.date.today()
        return cls.objects.filter(due_to_date__gte=today)

    @classmethod
    def get_all_user_tasks_from_today(cls, user_id):
        return cls._get_future_tasks().filter(owner=user_id)

    @classmethod
    def from_today_grouped_by(cls, owner, field):
        tasks_query = Task.get_all_user_tasks_from_today(owner).values().order_by(field)
        tasks_dict = defaultdict(list)
        dict_list = []

        for tasks_dictionary in tasks_query:
            dict_list.append(tasks_dictionary)
        for task_dict in dict_list:
            tasks_dict[task_dict[field]].append(task_dict)

        return dict(tasks_dict)

    @classmethod
    def user_tasks_count_by_date(cls, owner):
        user_tasks = cls.get_all_user_tasks_from_today(owner)
        return user_tasks.values('due_to_date').order_by('due_to_date').annotate(tasks_amount=Count('id'))

    def __str__(self):
        return self.title


class TaskForm(forms.Form):
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    due_to_date = forms.DateField()
    reminder = forms.DateTimeField(required=False)
    attached_file = forms.FileField(required=False)
