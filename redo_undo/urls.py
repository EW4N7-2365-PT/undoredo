from django.contrib import admin
from django.urls import path
from task.views import ListCreateTask, RetrieveUpdateTask

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tasks/', ListCreateTask.as_view()),
    path('tasks/<int:pk>/', RetrieveUpdateTask.as_view())

]
