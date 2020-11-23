
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, mixins,status,exceptions,generics,authentication,permissions
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied

from core.models import Bares
from barDetails.serializers import BarDetallesSerializer




# Esta funcion tiene post para encontrar el nombre del bar y si envias el id haces un get con los detalles del bar
class BarDetallesViewSet(viewsets.GenericViewSet,mixins.CreateModelMixin,mixins.RetrieveModelMixin,mixins.ListModelMixin):
    """  Detalles Generales del Bar"""

    serializer_class = BarDetallesSerializer
    queryset = Bares.objects.all()
    