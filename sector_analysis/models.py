from django.db import models

class ltp_tikrs(models.Model):
    tikr = models.CharField(max_length=64)
    ltp = models.FloatField()

# Create your models here.
class Holdings(models.Model):
    tikr = models.CharField(max_length=64)
    buy = models.FloatField()
    sl = models.FloatField()
    qty = models.IntegerField()
    t = models.FloatField()
    # entrydate = models.DateTimeField()
    # dt = models.DateTimeField()

    def __str__(self):
        return f"{self.tikr}|{self.buy}|{self.qty}|{self.sl}|{self.t}"
