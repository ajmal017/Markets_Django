from django.db import models
from django.utils import timezone
class ltp_tikrs(models.Model):
    tikr = models.CharField(max_length=64,primary_key = True)
    ltp = models.FloatField(default=0.0)
    def __str__(self):
        return f"{self.tikr}|{self.ltp}"


from datetime import datetime
# Create your models here.
class Holdings(models.Model):
    tikr = models.CharField(max_length=64)
    buy = models.FloatField()
    sl = models.FloatField()
    qty = models.IntegerField()
    t = models.FloatField() 
    entrydate = models.DateTimeField(default=datetime.now, blank=True)
    sell = models.FloatField(default=0.0)
    sell_status = models.BooleanField(default=False)
    exitdate = models.DateTimeField(default=datetime.now, blank=True)
    def __str__(self):
        return f"{self.tikr}|{self.buy}|{self.qty}|{self.sl}|{self.t}|{self.entrydate}|{self.sell_status}|{self.sell}|{self.exitdate}"
