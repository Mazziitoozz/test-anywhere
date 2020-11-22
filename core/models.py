from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxValueValidator,RegexValidator,MinValueValidator
# from django.contrib.postgres.fields import ArrayField, IntegerRangeField
# from django.contrib.postgres.validators import RangeMinValueValidator, RangeMaxValueValidator
from django.conf import settings

#Create your models here.
class UserManager(BaseUserManager):

    def create_user(self,email,password,is_owner=False,**extra_fields): #We can add the fields we want
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Email Missing')
        user = self.model(email = self.normalize_email(email), **extra_fields) # normalize the email
        user.is_owner=is_owner       # if you want to modify some column in the db you can do like that
        user.set_password(password)  # encript  password
        user.save(using = self._db)  # we use the default db in our settings, if we want to use another sb we should specify
        return user
    
    def create_superuser(self,email,password,**extra_fields):
        """Creates and saves a new superuser"""
        user = self.create_user(email,password,**extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser,PermissionsMixin):
    """ Custom user model that uses email instead of username"""
    username = models.CharField(max_length = 255,unique = True,validators=[RegexValidator(regex=r'^[a-zA-Z0-9]+$')])                  
    email =  models.EmailField(max_length = 255, unique = True)       # Maybe the email could be different for the same university, we will see
    is_active = models.BooleanField(default = True)
    is_owner = models.BooleanField(default = False)     # Owners will have different interface
    is_staff = models.BooleanField(default = False)

    # define the user manager class for User
    objects = UserManager()

    # In case we use email necessary to use the django authentication framework: this field is used as username
    USERNAME_FIELD  =   'username'
    REQUIRED_FIELDS = ['email']
        

class Bares(models.Model):
    """Bar info"""
    nombre = models.CharField(max_length = 60,validators=[RegexValidator(regex=r'^[a-zA-Z0-9 ]+$', message='Enter a valid value')])
    ubicacion = models.CharField(max_length = 100,validators=[RegexValidator(regex=r'^[a-zA-Z0-9 ]+$', message='Enter a valid value')]) 
    web =  models.CharField(max_length = 50,null=True) 
    telefono =models.PositiveIntegerField(null = True,validators=[RegexValidator(regex=r'^[0-9]+$', message='Enter a valid value',),MaxValueValidator(999999999)])
    apertura = models.TimeField(null = True) 
    cierre = models.TimeField(null = True) 
    user  = models.ForeignKey( settings.AUTH_USER_MODEL,null=True, on_delete = models.SET_NULL)  # settings.User==User but i prefer to write like that becasue is more dinamic

    def __str__(self):
        return str(self.nombre)

class Categorias(models.Model):
    ''' Dishes' categories '''
    categoria = models.CharField(unique = True,max_length=30,validators=[RegexValidator(regex=r'^[a-zA-Z ]+$', message='Enter a valid value')])
    
    def __str__(self):
        return self.categoria

class PlatosCategorias(models.Model):
    ''' Dishes with category '''
    categoria = models.ForeignKey(Categorias, on_delete = models.CASCADE) # Cambiar
    bar = models.ForeignKey(Bares,on_delete = models.CASCADE) # Cambiar
    plato = models.CharField(max_length=50)
    precio = models.PositiveIntegerField(validators=[RegexValidator(regex=r'^[0-9]+$', message='Enter a valid value',),MaxValueValidator(9999)])
    descripcion = models.CharField(max_length=250,null = True)
    celiaco = models.BooleanField(default=False)
    vegano = models.BooleanField(default=False)
    vegetariano = models.BooleanField(default=False)
    user  = models.ForeignKey( settings.AUTH_USER_MODEL,null=True, on_delete = models.SET_NULL)  # settings.User==User but i prefer to write like that becasue is more dinamic
    #Also we use null=True because we use set_null. Maybe we delete the user but we want to keep his dishes or ratings.
    
    def __repr__(self):
        return str(self.__dict__)

class PlatosValoraciones(models.Model):
    ''' Valoraciones de los usuarios de los platos'''
    user  = models.ForeignKey( settings.AUTH_USER_MODEL,null=True, on_delete = models.SET_NULL)  #we use null=True because we use set_null. Maybe we delete the user but we want to keep his dishes or ratings.
    plato  = models.ForeignKey( PlatosCategorias, on_delete = models.CASCADE)  
    valoracion = models.PositiveIntegerField(validators=[RegexValidator(regex=r'^[1-5]+$', message='Enter a valid value',),MaxValueValidator(5)])
    
    # Does not work
    def __repr__(self):
        return str(self.plato)

class MenuBar(models.Model):
    '''Menus de los bares'''
    plato = models.CharField(max_length=50)
    posicion = models.PositiveIntegerField(validators=[RegexValidator(regex=r'^[1-3]+$', message='Enter a valid value',),MaxValueValidator(3)])
    celiaco = models.BooleanField(default=False)
    vegano = models.BooleanField(default=False)
    vegetariano = models.BooleanField(default=False)
    # Día
    dia = models.DateField()
    bar = models.ForeignKey(Bares, on_delete = models.CASCADE)
    user  = models.ForeignKey( settings.AUTH_USER_MODEL,null=True, on_delete = models.SET_NULL)  # settings.User==User but i prefer to write like that becasue is more dinamic

class MenuIncluye(models.Model):
    '''Complementos incluidos'''
    menuPrecio = models.DecimalField(max_digits=5,decimal_places=2)
    bebida = models.BooleanField(default=False)
    pan = models.BooleanField(default=False)
    postre = models.BooleanField(default=False)
    cafe = models.BooleanField(default=False)
    anotacion = models.CharField(null = True,max_length=350)
    dia = models.DateField()

    bar = models.ForeignKey(Bares, on_delete = models.CASCADE)
    user  = models.ForeignKey( settings.AUTH_USER_MODEL,null=True, on_delete = models.SET_NULL)  # settings.User==User but i prefer to write like that becasue is more dinamic
