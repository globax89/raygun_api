import uuid

from django.db import models

from base import utils
from registration.models import User


# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(to=User, on_delete=models.PROTECT, related_name="creator_organization")
    administrators = models.ManyToManyField(to=User, null=True, blank=True, related_name="admin_orgnizations")
    users = models.ManyToManyField(to=User, null=True, blank=True, related_name="users_organizations")


class Service(models.Model):
    def generate_ticket(self):
        return utils.generate_random_string(50).upper()

    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    ticket = models.CharField(default=generate_ticket, max_length=50)
