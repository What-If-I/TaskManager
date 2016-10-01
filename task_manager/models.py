import datetime

from django.contrib.auth.models import User
from django.db import models


# todo: reminder can't be higher than due_to_date
class Task(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name='Task')
    due_to_date = models.DateField(default=datetime.date.today(), verbose_name='Due to')
    description = models.TextField('Description')
    reminder = models.DateTimeField('Reminder', blank=True, null=True)
    attached_file = models.FileField(upload_to='uploads/', blank=True, null=True)
    is_done = models.BooleanField(default=False)

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
        today = datetime.date.today()
        return cls.objects.raw(
            """Select id, title, due_to_date, description, is_done
               From task_manager_task
               WHERE due_to_date >= '{0}' and owner_id={1}
               GROUP BY {2}
               ORDER BY due_to_date""".format(today, owner, field))

    def __str__(self):
        return self.title
