from django.db import models

# Create your models here.
class Holdings(models.Model):
    tikr = models.CharField(max_length=64)
    buy = models.FloatField()
    sl = models.FloatField()
    qty = models.IntegerField()