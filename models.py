import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.contrib import admin


class Truck(models.Model):
  name=models.CharField(max_length="100")
  description = models.CharField(max_length="200", null= True)
  profile_icon=models.URLField(blank=True)
  date_added = models.DateTimeField(default=datetime.datetime.now())
  id_str = models.CharField(max_length="100")
  truck_url = models.URLField(blank=True)
  geo_enabled = models.BooleanField(default=False)
  real_name=models.CharField(max_length="100")
  def __unicode__(self):
    return self.name

from tagging.models import Tag

class Hood(models.Model):
  name = models.CharField(max_length="80")
  location = models.CharField(max_length="250")
  tags = models.ManyToManyField(Tag)
  def __unicode__(self):
    return self.name


