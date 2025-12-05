from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import Managers
# Create your models here.
class UserRegisters(AbstractUser):
    username= None
    email= models.EmailField(unique=True, max_length=100)

    otp= models.CharField(max_length=6)
    is_verified= models.BooleanField(default=False)

    USERNAME_FIELD= 'email'
    REQUIRED_FIELDS= []


    objects= Managers()

    def __str__(self):
        return self.email