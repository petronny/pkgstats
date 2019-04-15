#!/bin/python3
from django.db import models

class Cache(models.Model):
    pkgname = models.CharField(max_length=50, default="")
    count = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)
