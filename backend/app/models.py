from django.db import models

# Create your models here.

class AppModel(models.Model):
    ultrasonic_state = models.CharField(max_length=3)
    face_data = models.CharField(max_length=3)
    light_reading = models.CharField(max_length=3)
