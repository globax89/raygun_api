import datetime

from rest_framework import serializers
from .models import ErrorLogObject, LogEvolution, LogObject, LogInstance, UserInteraction


class LogInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogInstance
        fields = ('timestamp', 'type', 'log')


class LogEvolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEvolution
        fields = ('timestamp', 'count')


class SimpleErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLogObject
        fields = (
            'ticket', 'timestamp', 'message', 'stacktrace', 'count')


class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = '__all__'


class ErrorLogSerializer(serializers.ModelSerializer):
    evolution = serializers.SerializerMethodField()
    capturedLogs = serializers.SerializerMethodField()
    timestamp = serializers.CharField(required=False)
    type = serializers.CharField(write_only=True, allow_blank=True)
    log = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)
    userInteractions = serializers.SerializerMethodField()

    def add_log_instance_to_log_object(self, log_obj, instance_data):
        timestamp = instance_data.get('timestamp') if 'timestamp' in instance_data else str(
            datetime.datetime.now())
        li = LogInstance(log_id=log_obj.id,
                         timestamp=timestamp,
                         type=instance_data.get('type', 'log'),
                         log=instance_data.get('log', '')
                         )
        li.save()

        try:
            evolution = LogEvolution.objects.get(log_id=log_obj.id, timestamp=timestamp)
        except LogEvolution.DoesNotExist:
            evolution = LogEvolution.objects.create(log_id=log_obj.id, timestamp=timestamp, count=0)

        evolution.count += 1
        evolution.save()

        log_obj.timestamp = datetime.datetime.now()
        log_obj.save()
        return li

    def get_evolution(self, obj):
        evolutions = LogEvolution.objects.filter(log_id=obj.id)
        evol_ser = LogEvolutionSerializer(evolutions, many=True)

        return evol_ser.data

    def get_capturedLogs(self, obj):
        cap_logs = LogInstance.objects.filter(log_id=obj.id)
        caplogs_ser = LogInstanceSerializer(cap_logs, many=True)

        return caplogs_ser.data

    def get_userInteractions(self, obj):
        userinteractions = UserInteraction.objects.filter(log_id=obj.id)
        ser = UserInteractionSerializer(userinteractions, many=True)

        return ser.data

    def create(self, validated_data):
        print(validated_data)
        try:
            obj = ErrorLogObject.objects.get(stacktrace=validated_data.get('stacktrace'),
                                             message=validated_data.get('message'),
                                             ticket=validated_data.get('ticket'))
        except ErrorLogObject.DoesNotExist:
            obj = ErrorLogObject.objects.create(stacktrace=validated_data.get('stacktrace'),
                                                message=validated_data.get('message'),
                                                ticket=validated_data.get('ticket'),
                                                timestamp=datetime.datetime.now())

        self.add_log_instance_to_log_object(obj, validated_data)



        return obj

    class Meta:
        model = ErrorLogObject
        fields = (
            'ticket', 'timestamp', 'message', 'stacktrace', 'evolution', 'capturedLogs', 'timestamp', 'type', 'log',
            'userInteractions')
        read_only_fields = ('timestamp', 'evolution', 'capturedLogs')
