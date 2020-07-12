from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .serializers import OrganizationSerializer, ServiceSerializer
from .models import Organization, Service
# Create your views here.
from rest_framework.views import APIView


class OrganizationView(APIView):
    model = Organization

    def get(self, request, org_name):
        org = get_object_or_404(self.model, name=org_name)
        ser = OrganizationSerializer(org)

        return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request):
        ser = OrganizationSerializer(data=request.data)
        if ser.is_valid():
            org = ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ServiceView(APIView):
    model = Service
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, org_name, ticket):
        service = get_object_or_404(self.model, ticket=ticket)
        ser = ServiceSerializer(service)

        return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request, org_name):
        org = get_object_or_404(Organization, name=request.data.get('organization'))
        user = request.user
        if not (user.is_staff or user in org.administrators.all()):
            return Response({"error": "only organization admins can create service"}, status=status.HTTP_403_FORBIDDEN)

        service = Service(organization=org, name=request.data.get('name'), description=request.data.get('description'))
        service.save()
        ser = ServiceSerializer(service)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    def delete(self, request, org_name, ticket):
        services = Service.objects.filter(organization__name=org_name, ticket=ticket)
        ser = ServiceSerializer(services, many=True)
        data = ser.data
        services.delete()
        return Response(data={'status': 'deleted', 'objects': data}, status=status.HTTP_200_OK)


class ServiceListView(APIView):
    model = Service
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, org_name):
        services = Service.objects.filter(organization__name=org_name)
        ser = ServiceSerializer(services, many=True)

        return Response(ser.data, status=status.HTTP_200_OK)
