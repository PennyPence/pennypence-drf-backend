from django.db import models

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=10)
    detail = models.TextField()