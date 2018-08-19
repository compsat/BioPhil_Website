from django.db import models

# Create your models here.

class Updates(models.Model):# to get the last 5 in the query order it by ID number in descending order , then get [0:4]
    updateText = models.CharField(max_length = 200)
    pub_date = models.DateTimeField('Date Published')
    def __str__(self):
        return self.updateText

