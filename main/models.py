from django.db import models
from django.utils import timezone


class CoreModel(models.Model):
    created = models.DateTimeField(
        'Создано',
        null=False,
        default=timezone.now,
        editable=False,
    )

    updated = models.DateTimeField(
        'Обновлено',
        null=False,
        auto_now=True,
    )

    class Meta:
        abstract = True
        ordering = ['-updated']
