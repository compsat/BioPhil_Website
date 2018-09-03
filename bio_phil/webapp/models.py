from django.db import models

class Updates(models.Model):# to get the last 5 in the query, order it by ID number in descending order, then get [0:4]
    update_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(verbose_name='Date Published')

    def __str__(self):
        return self.update_text

    class Meta:
    	ordering = ('pub_date',)