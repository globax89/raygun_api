from django.urls import path
from .views import OrganizationView, ServiceView, ServiceListView

from registration import views

app_name = "organization"

urlpatterns = [
    path('<org_name>/service/<ticket>/', ServiceView.as_view(), name='service_view_get'),
    path('<org_name>/service/', ServiceView.as_view(), name='service_view_post'),
    path('<org_name>/services/', ServiceListView.as_view(), name='service_view_list'),
    path('<org_name>/', OrganizationView.as_view(), name='org_view_get'),
    path('', OrganizationView.as_view(), name='org_view_post'),

]
