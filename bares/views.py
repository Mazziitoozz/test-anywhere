
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, mixins,status,exceptions,generics,authentication,permissions
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied

from core.models import Bares, Categorias,PlatosCategorias,MenuBar,MenuIncluye,PlatosValoraciones
from bares.serializers import BaresSerializer,CategoriasSerializer,PlatosCategoriasSerializer,MenuBarSerializer,MenuIncluyeSerializer,PlatosValoracionesSerializer
from user.serializers import AuthTokenSerializer

import datetime
import pytz 

#AUTHENTICATION
class MyAuthentication(authentication.TokenAuthentication):
    ''' Our own Authentication'''
    # We modified the function because we want check if the token was created in the last two hours
    def authenticate_credentials(self, key):
        model = self.get_model()  
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
        # This is required for the time comparison. We geet current utc time. Token use utc time
        utc_now = datetime.datetime.utcnow()
        utc_now = utc_now.replace(tzinfo=pytz.utc)
        #The user has 2 hours and after it he needs to refreshs
        if token.created < utc_now - datetime.timedelta(hours=8):
            raise exceptions.AuthenticationFailed('Token has expired')
        return (token.user, token)

class BaseViewset(viewsets.GenericViewSet,mixins.ListModelMixin):
    """ Base Viewset from Courses and students """
    permissions_classes = (permissions.IsAuthenticated,)#permissions.IsAuthenticated,) #permissions.IsAuthenticated,)
    authentication_classes = (MyAuthentication,) #AllowAny,MyAuthentication,)

    def mycheck_permissions(self,request):
            if(request.user.is_owner):
                return True
            raise PermissionDenied
#Bares
class CreateBarViewSet(BaseViewset,mixins.CreateModelMixin,mixins.ListModelMixin):
    """ Añade un bar y lista todos los bares que un usuario tiene"""
    serializer_class = BaresSerializer
    queryset = Bares.objects.all()

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        self.mycheck_permissions(self.request)                  # Solo el dueño puede crear
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        checkOwnerBar = Bares.objects.filter(user=serializer.validated_data['user'])
        if checkOwnerBar.exists():
            return Response(data="You are already the owner of a bar",status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class getBarUserIdViewSet(BaseViewset,mixins.ListModelMixin):
    """ Get el bar id que tiene el usuario """
    queryset = Bares.objects.all()
   
    def list(self, request, *args, **kwargs):
        self.mycheck_permissions(self.request) 
        if (self.queryset.filter(user=self.request.user)):
            bar_id = self.queryset.filter(user=self.request.user).values('id')[0]['id']
        else:
            bar_id= False
        user_id = self.request.user.id
        result = { 'user_id':user_id,'bar_id':bar_id}
        return Response(result)

class RetrieveUpdateBarViewSet(BaseViewset,generics.RetrieveUpdateDestroyAPIView):
    """ Editar los detalles del bar """
    serializer_class = BaresSerializer
    queryset = Bares.objects.all()
    # Only shows bar that the owner has and he cant update or delete the bar of other owner
    def get_queryset(self):
        self.mycheck_permissions(self.request)                  # Solo el dueño puede editar
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

#Categorias
class CategoriasViewSet(viewsets.GenericViewSet,mixins.ListModelMixin):
    """ Distintas categorias de los platos"""
    serializer_class = CategoriasSerializer
    queryset = Categorias.objects.all()
    
# Platos de la carta
class PlatosCategoriasViewSet(mixins.CreateModelMixin,generics.RetrieveUpdateDestroyAPIView,BaseViewset):
    """  Añadir o editar un plato a la carta"""

    serializer_class = PlatosCategoriasSerializer
    queryset = PlatosCategorias.objects.all()
    
    # Only shows bar that the owner has and he cant update or delete the bar of other owner
    def get_queryset(self):
        self.mycheck_permissions(self.request)                  # Solo el dueño puede editar
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        self.mycheck_permissions(self.request)                  # Solo el dueño puede crear
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
             
        # Check if the bar exists for this user. We check the name and the user_id. I also checked in the serializer although it is not necessary.
        checkBar =  Bares.objects.filter(nombre=str(serializer.validated_data['bar']),
                                         user_id=(self.request.user.id))  
        if not checkBar.exists():
            return Response(data="No eres el propietario del bar elegido",status=status.HTTP_400_BAD_REQUEST)
        # Evitar que halla un numero ilimitado de platos en la carta
        if len(PlatosCategorias.objects.filter(user_id=(self.request.user.id)))>250:
            return Response(data="Has excedido el numero de platos que se pueden tener en la carta",status=status.HTTP_400_BAD_REQUEST)     
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# Menu del dia
class MenuBarViewSet(mixins.CreateModelMixin,generics.RetrieveUpdateDestroyAPIView,BaseViewset):
    """  Menu del dia del bar"""

    serializer_class = MenuBarSerializer
    queryset = MenuBar.objects.all()
    
    # Only shows bar that the owner has and he cant update or delete the bar of other owner
    def get_queryset(self):
        self.mycheck_permissions(self.request)                  # Solo el dueño puede editar
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        self.mycheck_permissions(self.request)                  # Solo el dueño puede crear
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Check if the bar exists for this user. We check the name and the user_id. I also checked in the serializer although it is not necessary.
        checkBar =  Bares.objects.filter(nombre=str(serializer.validated_data['bar']),
                                         user_id=(self.request.user.id))  
        if not checkBar.exists():
            return Response(data="He is not the owner of the bar chosed",status=status.HTTP_400_BAD_REQUEST)
        
        # Maximo de platos a añadir en el menu del dia
        if len(MenuBar.objects.filter(user=self.request.user,dia=request.data['dia']))>30:
            return Response(data="No puedes añadir más platos a este menu del dia",status=status.HTTP_400_BAD_REQUEST)

        # Delete from the database the old menus
        MenuBar.objects.filter(user=self.request.user,dia__lt=datetime.datetime.today()).delete()
     
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
  
# Menu Incluye
class MenuIncluyeViewSet(mixins.CreateModelMixin,generics.RetrieveUpdateDestroyAPIView,BaseViewset):
    """  Añadir Precio del menu y lo que incluye"""

    serializer_class = MenuIncluyeSerializer
    queryset = MenuIncluye.objects.all()
    
    # Only shows bar that the owner has and he cant update or delete the bar of other owner
    def get_queryset(self):
        self.mycheck_permissions(self.request)                  # Solo el dueño puede editar
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        print(request.data)
        self.mycheck_permissions(self.request)                  # Solo el dueño puede crear
        serializer = self.get_serializer(data=request.data)
        print(serializer)
        serializer.is_valid(raise_exception=True)
        # Check if the bar exists for this user. We check the name and the user_id. I also checked in the serializer although it is not necessary.
        checkBar =  Bares.objects.filter(nombre=str(serializer.validated_data['bar']),
                                         user_id=(self.request.user.id))  
        if not checkBar.exists():
            return Response(data="He is not the owner of the bar chosed",status=status.HTTP_400_BAD_REQUEST)

        if MenuIncluye.objects.filter(user_id=(self.request.user.id),dia=request.data['dia']).exists():
            updateMenuInc =MenuIncluye.objects.get(user_id=(self.request.user.id),dia=request.data['dia']).delete()
        
        # Delete from the database the old menus
        MenuIncluye.objects.filter(user=self.request.user,dia__lt=datetime.datetime.today()).delete()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
   
# Plato Review
class PlatosValoracionesViewSet(mixins.CreateModelMixin,BaseViewset):
    """  Añadir Valoraciones de los platos por los usuarios"""

    serializer_class = PlatosValoracionesSerializer
    queryset = PlatosValoraciones.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
   
        # Check if the user has already reviewed the dish
        checkUserReview =   PlatosValoraciones.objects.filter(plato=request.data['plato'],
                                         user_id=(self.request.user.id))  
        if checkUserReview.exists():
            previousReview = PlatosValoraciones.objects.get(plato=request.data['plato'],
                                         user_id=(self.request.user.id))
            previousReview.valoracion =request.data['valoracion']
            previousReview.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
   
    
 