from rest_framework.generics import ListCreateAPIView
from .serializers import TaskSerializer
from .models import Task
from app.views import RetrieveUpdateUndoRedoAPIView
from app.mixins import VersionMixin
from reversion.views import RevisionMixin


class ListCreateTask(ListCreateAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()


class RetrieveUpdateTask(VersionMixin, RevisionMixin, RetrieveUpdateUndoRedoAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
