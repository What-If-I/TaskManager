from django.contrib import admin
from .models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'due_to_date', 'reminder', 'owner']
    search_fields = ['title']
    list_filter = ['owner']

admin.site.register(Task, TaskAdmin)
