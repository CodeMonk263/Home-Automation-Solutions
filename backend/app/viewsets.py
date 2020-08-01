from .serializers import *
import asyncio
from .models import AppModel
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from asgiref.sync import sync_to_async
import os
import sys

class AppSerializerViewset(viewsets.ModelViewSet):

    queryset = AppModel.objects.all()
    serializer_class = AppSerialiser
    
    @action(detail=False, methods=['get','post'])
    def method_update(self, request, pk=None):
        if request.method == 'GET':
            AppModel.objects.all().delete()
            path_to_status = os.path.dirname(os.path.realpath(sys.argv[0]))+"/mqtt_client/data/status.txt"
            path_to_cam = os.path.dirname(os.path.realpath(sys.argv[0]))+"/mqtt_client/data/cam.txt"
            path_to_ldr = os.path.dirname(os.path.realpath(sys.argv[0]))+"/mqtt_client/data/ldr.txt"
            with open(path_to_status, "r") as f:
                status_payload = f.read()
            with open(path_to_cam, "r") as f:
                cam_payload = f.read()
            with open(path_to_ldr, "r") as f:
                ldr_payload = f.read()
            AppModel.objects.create(ultrasonic_state=status_payload, face_data=cam_payload, light_reading=ldr_payload)
            data = AppModel.objects.first()
            serializer = AppSerialiser(data=data.__dict__)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'POST':
            AppModel.objects.all().delete()
            ultrasonic_state = request.data["ultrasonic_state"]
            face_data = request.data["face_data"]
            ldr_data = request.data["light_reading"]
            path_to_status = os.path.dirname(os.path.realpath(sys.argv[0]))+"/mqtt_client/data/status.txt"
            path_to_cam = os.path.dirname(os.path.realpath(sys.argv[0]))+"/mqtt_client/data/cam.txt"
            path_to_ldr = os.path.dirname(os.path.realpath(sys.argv[0]))+"/mqtt_client/data/ldr.txt"
            with open(path_to_status, "w") as f:
                f.write(ultrasonic_state)
            with open(path_to_cam, "w") as f:
                f.write(face_data)
            with open(path_to_ldr, "w") as f:
                f.write(ldr_data)
            AppModel.objects.create(ultrasonic_state=ultrasonic_state, face_data=face_data, light_reading=ldr_data)
            data = AppModel.objects.first()
            serializer = AppSerialiser(data=data.__dict__)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
