import datetime

from django.shortcuts import render, get_object_or_404
from rest_framework import views, status
# Create your views here.
from rest_framework.response import Response

from .models import LogObject, LogInstance, LogEvolution, ErrorLogObject, UserInteraction
from .serializers import ErrorLogSerializer, SimpleErrorLogSerializer


class ErrorLogView(views.APIView):
    model = ErrorLogObject

    def get(self, request, id):
        instance = get_object_or_404(self.model, id=id)
        ser = ErrorLogSerializer(instance)

        return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request):
        errobj_ser = ErrorLogSerializer(data=request.data)

        if errobj_ser.is_valid():
            obj = errobj_ser.save()
            userinteractions = request.data.get('userInteractions')
            if userinteractions:
                interactions = UserInteraction.objects.filter(log_id=obj.id)
                if not interactions.exists():
                    for d in userinteractions:
                        o = UserInteraction.objects.create(log_id=obj.id, innerText=d.get('innertext'),
                                                           element=d.get('element'), elementId=d.get('elementId'),
                                                           location=d.get('location'), timestamp=d.get('timestamp', str(datetime.datetime.now())))
                        errobj_ser = ErrorLogSerializer(obj)
            return Response(errobj_ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(errobj_ser.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ErrorLogListView(views.APIView):
    model = ErrorLogObject

    def get(self, request, ticket):
        objects = ErrorLogObject.objects.filter(ticket=ticket)
        ser = SimpleErrorLogSerializer(objects, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)
