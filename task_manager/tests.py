import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.test import Client
from django.db import models

from .models import Task


def create_user(username):
    return User.objects.create_user(username=username, email='', password='')


def create_task(owner, title, days, remind_days):
    """
    Creates a task with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    remind_time = timezone.now() + datetime.timedelta(days=remind_days)

    return Task.objects.create(
        owner=owner,
        title=title,
        due_to_date=time,
        description='Test description',
        reminder=remind_time,
        attached_file='uploads/test_file.txt',
    )


class TasksView(TestCase):
    def test_index_view_no_tasks(self):
        response = self.client.get(reverse('task_manager:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No tasks to be done.')
        self.assertQuerysetEqual(response.context['user_tasks'], [])

    def test_index_view_outdated_tasks(self):
        """
        Old tasks should not be displayed.
        """
        bob = create_user('Bob')
        self.client.login(username='Bob', password='')

        create_task(owner=bob, title='Bob task', days=-1, remind_days=0)

        response = self.client.get(reverse('task_manager:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No tasks to be done.')
        self.assertQuerysetEqual(response.context['user_tasks'], [])

    def test_index_view_future_tasks(self):
        """
        Task >= today should be displayed.
        """
        bob = create_user('Bob')
        self.client.login(username='Bob', password='')

        create_task(owner=bob, title='Bob today task', days=0, remind_days=0)
        create_task(owner=bob, title='Bob future task', days=1, remind_days=0)
        response = self.client.get(reverse('task_manager:index'))

        self.assertQuerysetEqual(
            response.context['user_tasks'],
            ["<Task: Bob today task>", "<Task: Bob future task>"], ordered=False  # todo: fix this shit
        )

    def test_view_task_of_other_user_not_visible(self):
        """
        User can see ONLY his tasks.
        """
        bob = create_user('Bob')
        charlie = create_user('charlie')
        self.client.login(username='Bob', password='')

        create_task(owner=bob, title='Bob today task', days=1, remind_days=1)
        create_task(owner=charlie, title='Charlie task', days=1, remind_days=1)

        bob_response = self.client.get(reverse('task_manager:index'))

        self.assertQuerysetEqual(
            bob_response.context['user_tasks'], ["<Task: Bob today task>"]
        )

    def test_count_by_date(self):
        """
        Task.count_by_date method test.
        """
        bob = create_user('Bob')

        create_task(owner=bob, title='Bob today first task', days=0, remind_days=1)
        create_task(owner=bob, title='Bob today second task', days=0, remind_days=1)
        create_task(owner=bob, title='Bob tomorrow first task', days=1, remind_days=1)
        create_task(owner=bob, title='Bob tomorrow second task', days=1, remind_days=1)
        create_task(owner=bob, title='Bob future task', days=4, remind_days=1)

        print(Task.user_tasks_count_by_date(bob))

        self.assertQuerysetEqual(Task.user_tasks_count_by_date(bob),
                                 [
                                     "{'tasks': 2, 'due_to_date': datetime.date(2016, 10, 4)}",
                                     "{'tasks': 2, 'due_to_date': datetime.date(2016, 10, 5)}",
                                     "{'tasks': 1, 'due_to_date': datetime.date(2016, 10, 8)}",
                                 ]
                                 )
