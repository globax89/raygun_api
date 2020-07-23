from django.urls import path
from .views import ErrorLogView, ErrorLogListView

from registration import views

app_name = "logmanager"

urlpatterns = [
    path('error/<ticket>/', ErrorLogListView.as_view(), name="error_list"),
    path('error/<ticket>/<id>', ErrorLogView.as_view(), name='error_get'),
    path('error/', ErrorLogView.as_view(), name='error_post'),

]
