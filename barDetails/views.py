
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, mixins,status,exceptions,generics,authentication,permissions
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied

from core.models import Bares, Categorias,PlatosCategorias,MenuBar,MenuIncluye,PlatosValoraciones
from barDetails.serializers import BarDetallesSerializer
from user.serializers import AuthTokenSerializer
from bares.serializers import PlatosCategoriasSerializer

import datetime
import pytz 
import statistics 

# Esta funcion tiene post para encontrar el nombre del bar y si envias el id haces un get con los detalles del bar
class BarDetallesViewSet(viewsets.GenericViewSet,mixins.CreateModelMixin,mixins.RetrieveModelMixin):
    """  Detalles Generales del Bar"""

    serializer_class = BarDetallesSerializer
    queryset = Bares.objects.all()
    
    # Post method para recibir el id del bar
    def create(self, request, *args, **kwargs):
        Bares=self.queryset.filter(nombre=request.data['nombre'])
        baresArr=[]
        
        for bar in Bares:
            barInfo={}
            # Si el bar tiene menu mostraremos el menu
            if MenuBar.objects.filter(bar_id=bar.id): 
                barInfo['id']=bar.id
                barInfo['nombre'] = bar.nombre
                barInfo['ubicacion'] = bar.ubicacion
                barInfo['primeros'] = []
                barInfo['segundos'] = []
                barInfo['postres'] = []
                barInfo['incluye'] = MenuIncluye.objects.filter(bar_id = bar.id).values('menuPrecio','bebida','pan','postre','cafe')

                for plato in MenuBar.objects.filter(bar_id = bar.id).values('plato','posicion','celiaco','vegano','vegetariano','dia'):
                    if plato['posicion']==1: 
                        barInfo['primeros'].append(plato['plato'])
                    elif plato['posicion']==2: 
                        barInfo['segundos'].append(plato['plato'])
                    else:
                        barInfo['postres'].append(plato['plato']) 

            # Si el bar no tiene menu mostraremos los detalles
            else:
                barInfo['id']=bar.id
                barInfo['nombre']=bar.nombre
                barInfo['ubicacion']=bar.ubicacion
                barInfo['web']=bar.web
                barInfo['telefono']=bar.telefono
                barInfo['apertura']=bar.apertura
                barInfo['cierre']=bar.cierre
            baresArr.append(barInfo)
        return Response(baresArr)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        barData=serializer.data                     # Array con los datos del bar
        # MENU
        menuPlatosModel=MenuBar.objects.filter(bar_id=self.kwargs['pk'])
        diaMenu ={}
        if menuPlatosModel: 
            diaPlato = datetime.datetime.now()
            for i in range(7):                              # Mostraremos el menu de los 7 dias siguientes 
                barMenu={}                                  # Menu del bar
                # Inicializamos las lists
                barMenu['primeros'] = []
                barMenu['segundos'] = []
                barMenu['postres'] = []
                barMenu['incluye'] = MenuIncluye.objects.filter(bar_id = self.kwargs['pk'],dia=diaPlato).values('menuPrecio','bebida','pan','postre','cafe','anotacion')
                # Filtramos por dia
                for plato in menuPlatosModel.filter(dia=diaPlato).values('id','plato','posicion','celiaco','vegano','vegetariano'):
                    res = {key: plato[key] for key in plato.keys() 
                                & {'id', 'plato','vegano','celiaco','vegetariano'}} # Necesario para insertarlo en forma de object
                # Clasificamos los platos
                    if plato['posicion']==1: 
                        barMenu['primeros'].append(res)
                    elif plato['posicion']==2: 
                        barMenu['segundos'].append(res)
                    else:
                        barMenu['postres'].append(res) 
                diaMenu[diaPlato.strftime("%Y-%m-%d")]=barMenu              # Convertimos a string el dia para ponerlo como key
                diaPlato = diaPlato + datetime.timedelta(days=1)            # Pasamos al dia siguiente

        barData['menu']=diaMenu
        # CARTA
        queryset1 = PlatosCategorias.objects.filter(bar_id = self.kwargs['pk'])
        serializerCarta = PlatosCategoriasSerializer(queryset1,many=True)
        barData['carta']=serializerCarta.data
        # VALORACIONES
        for plato in barData['carta']:
            valoraciones = PlatosValoraciones.objects.filter(plato=plato['id']).values_list(('valoracion'),flat=True).order_by('id')
            # Enviamos directamente la media de las valoraciones y el numero de personas que lo han evaluado
            if valoraciones:
                plato['meanVal'] = round(statistics.mean(valoraciones),1)        # media de las valoraciones
                plato['numVal'] = len(valoraciones)                              # numero de valoraciones
            else: 
                plato['meanVal'] = 0     
                plato['numVal'] = 0             
        return Response(barData)