from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxValueValidator,RegexValidator,MinValueValidator
# from django.contrib.postgres.fields import ArrayField, IntegerRangeField
# from django.contrib.postgres.validators import RangeMinValueValidator, RangeMaxValueValidator
from django.conf import settings


class Bares(models.Model):
    """Bar info"""
    nombre = models.CharField(max_length = 60,validators=[RegexValidator(regex=r'^[a-zA-Z0-9 ]+$', message='Enter a valid value')])
    ubicacion = models.CharField(max_length = 100,validators=[RegexValidator(regex=r'^[a-zA-Z0-9 ]+$', message='Enter a valid value')]) 
    web =  models.CharField(max_length = 50,null=True) 
    telefono =models.PositiveIntegerField(null = True,validators=[RegexValidator(regex=r'^[0-9]+$', message='Enter a valid value',),MaxValueValidator(999999999)])
    apertura = models.TimeField(null = True) 
    cierre = models.TimeField(null = True) 

    def __str__(self):
        return str(self.nombre)

