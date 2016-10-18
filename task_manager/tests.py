import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.test import Client
from django.db import models

from .models import Task


def create_user(username, password=""):
    return User.objects.create_user(username=username, email='', password=password)


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


class AuthorisationTest(TestCase):
    def redirect_unauthorised_user(self):
        response = self.client.get(reverse('task_manager:index'))
        self.assertEqual(response.status_code, 302)

    def successfully_logged_in(self):
        create_user(username='Bob', password='123')
        response = self.client.post('/login/', {'username': 'Bob', 'password': '123'}, follow=True)

        self.assertRedirects(response, '/')

    def auth_failed(self):
        create_user(username='Bob', password='123')
        response = self.client.post('/login/', {'username': 'Bob', 'password': ''}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your username and password didn't match. Please try again.")


class TasksView(TestCase):
    """Bob exist by default and logged in"""
    def setUp(self):
        self.user_bob = create_user(username='Bob', password='123')
        self.client.login(username='Bob', password='123')

    def test_index_view_no_tasks(self):
        self.client.login(username='Bob', password='')

        response = self.client.get(reverse('task_manager:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['tasks_by_days'], [])

    def test_index_view_outdated_tasks(self):
        """
        Old tasks should not be displayed.
        """
        create_task(owner=self.user_bob, title='Bob task', days=-1, remind_days=0)

        response = self.client.get(reverse('task_manager:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['tasks_by_days'], [])

    def test_index_view_future_tasks(self):
        """
        Task >= today should be displayed.
        """
        self.client.login(username='Bob', password='')

        create_task(owner=self.user_bob, title='Bob today task', days=0, remind_days=0)
        create_task(owner=self.user_bob, title='Bob future task', days=1, remind_days=0)
        create_task(owner=self.user_bob, title='Bob future task2', days=1, remind_days=0)
        response = self.client.get(reverse('task_manager:index'))

        self.assertQuerysetEqual(
            response.context['tasks_by_days'],
            [
                {'tasks_amount': 1, 'due_to_date': datetime.date.today()},
                {'due_to_date': datetime.date.today()+datetime.timedelta(days=1), 'tasks_amount': 2},
            ], transform=dict,
        )

    def test_view_task_of_other_user_not_visible(self):
        """
        User can see ONLY his tasks.
        """
        user_charlie = create_user('charlie')

        create_task(owner=user_charlie, title='Charlie\'s task', days=1, remind_days=1)

        bob_response = self.client.get(reverse('task_manager:index'))
        print(bob_response.context)

        self.assertQuerysetEqual(
            bob_response.context['object_list'], {}, transform=dict,)

    def test_count_by_date(self):
        """
        Task.count_by_date method test.
        """
        create_task(owner=self.user_bob, title='Bob today first task', days=0, remind_days=1)
        create_task(owner=self.user_bob, title='Bob today second task', days=0, remind_days=1)
        create_task(owner=self.user_bob, title='Bob tomorrow first task', days=1, remind_days=1)
        create_task(owner=self.user_bob, title='Bob tomorrow second task', days=1, remind_days=1)
        create_task(owner=self.user_bob, title='Bob future task', days=4, remind_days=1)

        self.assertQuerysetEqual(Task.user_tasks_count_by_date(self.user_bob),
                                 [
                                     {'tasks_amount': 2, 'due_to_date': datetime.date.today()},
                                     {'tasks_amount': 2, 'due_to_date': datetime.date.today() + datetime.timedelta(1)},
                                     {'tasks_amount': 1, 'due_to_date': datetime.date.today() + datetime.timedelta(4)},
                                 ], transform=dict
                                 )
