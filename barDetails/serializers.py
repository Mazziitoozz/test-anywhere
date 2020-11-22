
from rest_framework import serializers,status
from core.models import Bares,User, Categorias,PlatosCategorias,MenuBar,MenuIncluye,PlatosValoraciones
import re
from rest_framework.response import Response

class BarDetallesSerializer(serializers.ModelSerializer):
    """Serializer for the BarDetails"""
    class Meta:
        model = Bares
        fields = ('id','nombre','ubicacion','web','telefono','apertura','cierre')
        read_only_fields =('id',)
