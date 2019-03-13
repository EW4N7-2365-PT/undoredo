from django.db import models
import reversion


@reversion.register()
class Task(models.Model):
    name = models.CharField(max_length=255)
    votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
