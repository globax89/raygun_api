import datetime

from django.db import models
from organization import models as org_models


# Create your models here.

class LogInstance(models.Model):
    log_id = models.IntegerField(db_index=True)
    timestamp = models.CharField(max_length=500)
    type = models.CharField(max_length=300)
    log = models.TextField()

    class Meta:
        ordering = ('log_id', '-timestamp',)


class LogObject(models.Model):
    ticket = models.CharField(max_length=org_models.Service._meta.get_field('ticket').max_length)
    timestamp = models.DateTimeField(auto_now=True)
    message = models.TextField()

    class Meta:
        ordering = ('-timestamp',)

    @property
    def count(self):
        return LogInstance.objects.filter(log_id=self.id).count()

    def __str__(self):
        return f"{self.id} - {self.ticket} - {self.message}"


class ErrorLogObject(LogObject):
    stacktrace = models.TextField()


class UserInteraction(models.Model):

    def get_cur_str_time():
        return str(datetime.datetime.now())

    log_id = models.IntegerField()
    elementId = models.CharField(max_length=200, null=True, blank=True)
    element = models.CharField(max_length=200, null=True, blank=True)
    innerText = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    timestamp = models.CharField(max_length=200, default=get_cur_str_time, null=True, blank=True)

    class Meta:
        ordering = ('log_id', 'timestamp')


class LogEvolution(models.Model):
    log_id = models.IntegerField(db_index=True)
    timestamp = models.CharField(max_length=500)
    count = models.IntegerField(default=1)

    class Meta:
        ordering = ('-timestamp',)
