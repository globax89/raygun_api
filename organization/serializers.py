from django.shortcuts import get_object_or_404

from .models import Organization, Service
from rest_framework import serializers
from registration.serializers import CreateUserSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    creator = CreateUserSerializer()
    administrators = serializers.SerializerMethodField(read_only=True)
    users = serializers.SerializerMethodField(read_only=True)

    def get_administrators(self, obj: Organization):
        administrators_ser = CreateUserSerializer(obj.administrators.all(), many=True)

        return administrators_ser.data

    def get_users(self, obj: Organization):
        users_ser = CreateUserSerializer(obj.users.all(), many=True)

        return users_ser.data

    def create(self, validated_data: dict):
        user_data = validated_data.get('creator')
        del validated_data['creator']
        creator_ser = CreateUserSerializer(data=user_data)
        if creator_ser.is_valid():
            creator = creator_ser.save()
        else:
            raise ValueError("Creator ser validation failed")

        org = Organization(creator=creator, **validated_data)

        org.save()

        return org

    class Meta:
        model = Organization
        fields = ('name', 'identifier', 'creator', 'administrators', 'users')
        read_only_fields = ('identifier',)


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ('organization', 'name', 'description', 'ticket')
        read_only_fields = ('ticket',)
