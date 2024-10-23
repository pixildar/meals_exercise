from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Meal(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    thumbnail = models.URLField() # the advantage over CharField is that django validates is automatically
    #metadata = models.JSONField() # json.JSONEncoder (&decoder) are used by default on django 
    

class Review(models.Model):

    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    text = models.TextField(blank=False)
    score = models.PositiveSmallIntegerField(
        validators = [
            MinValueValidator(1, message="Score cannot be less than 1"),
            MaxValueValidator(10, message="Score cannot be greater than 10")
            ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
