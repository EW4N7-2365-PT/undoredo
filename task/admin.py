from django.contrib import admin
from .models import Task
from reversion.admin import VersionAdmin

admin.site.register(Task, VersionAdmin)
