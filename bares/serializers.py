
from rest_framework import serializers,status
from core.models import Bares,User, Categorias,PlatosCategorias,MenuBar,MenuIncluye,PlatosValoraciones
import re
from rest_framework.response import Response
import datetime
class BaresSerializer(serializers.ModelSerializer):
    """Serializer for the Bares"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) # we send the user as a hiddenfield
    class Meta:
        model = Bares
        fields = ('id','nombre','ubicacion','web','telefono','apertura','cierre','user')
        read_only_fields =('id',)

    # Remove extra spaces 
    def validate_nombre(self,value):
        name = re.sub(' +', ' ',value)        
        return name

    def validate_ubicacion(self,value):
        name = re.sub(' +', ' ',value)        
        return name

class CategoriasSerializer(serializers.ModelSerializer):
    ''' Serializer for categorias '''
    class Meta:
        model = Categorias
        fields = ('id','categoria')
        read_only_fields = ('id',)

class PlatosCategoriasSerializer(serializers.ModelSerializer):
    ''' Serializer for categorias y platos '''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) # we send the user as a hiddenfield
    bar = serializers.HiddenField(default=1) # we send the bar as a hiddenfield

    class Meta:
        model = PlatosCategorias
        fields = ('id','plato','categoria','precio','descripcion','celiaco','vegetariano','vegano','bar','user')
        read_only_fields = ('id',)

    # We check if the user is the owner of the bar
    def validate_bar(self,value):
        value = Bares.objects.filter(user_id=(self.context['request'].user.id))  
        checkBar =  Bares.objects.filter(nombre=value[0],
                                         user_id=(self.context['request'].user.id))  
        if not checkBar.exists():
            raise serializers.ValidationError("He is not the owner of the bar chosed")
       
        return value[0]
    

class MenuBarSerializer(serializers.ModelSerializer):
    ''' Serializer for Menu Bar'''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) # we send the user as a hiddenfield
    bar = serializers.HiddenField(default=1) # we send the bar as a hiddenfield

    class Meta:
        model = MenuBar
        fields = ('id','plato','posicion','celiaco','vegetariano','vegano','dia','bar','user')
        read_only_fields = ('id',)

    # We check if the user is the owner of the bar. We check the name and the user_id
    def validate_bar(self,value):
        value = Bares.objects.filter(user_id=(self.context['request'].user.id))  

        checkBar =  Bares.objects.filter(nombre=value[0],
                                         user_id=(self.context['request'].user.id))  
        if not checkBar.exists():
            raise serializers.ValidationError("He is not the owner of the bar chosed")
       
        return value[0]
    # Comprobarmos si el dia insertado es valido
    def validate_dia(self,value):
        currentDate = datetime.datetime.today().date()
        if currentDate > value:
            raise serializers.ValidationError("No puedes elegir una fecha que ya ha pasado")
        if (value-currentDate).days>7:
            raise serializers.ValidationError("Elige una fecha mas proxima")
        return value

class MenuIncluyeSerializer(serializers.ModelSerializer):
    ''' Serializer for Menu Bar'''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) # we send the user as a hiddenfield
    bar = serializers.HiddenField(default=1) # we send the bar as a hiddenfield

    class Meta:
        model = MenuIncluye
        fields = ('id','menuPrecio','bebida','pan','postre','anotacion','dia','bar','user','cafe')
        read_only_fields = ('id',)

    # We check if the user is the owner of the bar
    def validate_bar(self,value):
        value = Bares.objects.filter(user_id=(self.context['request'].user.id))  

        checkBar =  Bares.objects.filter(nombre=value[0],
                                         user_id=(self.context['request'].user.id))  
        if not checkBar.exists():
            raise serializers.ValidationError("He is not the owner of the bar chosed")
       
        return value[0]

    def validate_dia(self,value):
        currentDate = datetime.datetime.today().date()
        if currentDate > value:
            raise serializers.ValidationError("No puedes elegir una fecha que ya ha pasado")
        if (value-currentDate).days>7:
            raise serializers.ValidationError("Elige una fecha mas proxima")
        return value

class PlatosValoracionesSerializer(serializers.ModelSerializer):
    ''' Serializer for dishes reviews'''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) # we send the user as a hiddenfield

    class Meta:
        model = PlatosValoraciones
        fields = ('id','plato','valoracion','user')
        read_only_fields = ('id',)

