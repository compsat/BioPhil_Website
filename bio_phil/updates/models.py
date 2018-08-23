from django.db import models

# Create your models here.

class Updates(models.Model):# to get the last 5 in the query, order it by ID number in descending order, then get [0:4]
    update_text = models.CharField(max_length = 200)
    pub_date = models.DateTimeField('Date Published')
    def __str__(self):
        return self.update_text

# docker-compose run web python bio_phil/manage.py makemigrations
