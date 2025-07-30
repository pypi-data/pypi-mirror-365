from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Vue(models.Model):
    vues = models.PositiveIntegerField(default=0)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.content_type} - {self.object_id} : {self.vues} vues"

    def increment_vues(self):
        self.vues += 1
        self.save()


class Article(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()

    def __str__(self):
        return self.titre
