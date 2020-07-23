from django.contrib import admin
from .models import LogInstance, ErrorLogObject, UserInteraction
# Register your models here.

admin.site.register((
    LogInstance,
    ErrorLogObject,
    UserInteraction
))
