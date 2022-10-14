from django.db import models


# Create your models here.
class Poetry(models.Model):
    title = models.CharField(max_length=64, default="")
    rhythmic = models.CharField(max_length=64, default="")
    author = models.CharField(max_length=16, default="")
    paragraphs = models.TextField(max_length=3000, default="")


class Rule(models.Model):
    keyword1 = models.CharField(max_length=64)
    keyword2 = models.CharField(max_length=64)
    mode = models.CharField(max_length=64)
    topic_description = models.CharField(max_length=256)
    key_description = models.CharField(max_length=256)
