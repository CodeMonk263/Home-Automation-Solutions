from rest_framework import serializers
from .models import AppModel

class AppSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AppModel
        fields = ('ultrasonic_state', 'face_data', 'light_reading')