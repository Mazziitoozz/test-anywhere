from django.urls import path,include

from bares import views
from rest_framework.routers import DefaultRouter

# Use Viewsets
router = DefaultRouter()
# Bares
router.register('editBar', views.RetrieveUpdateBarViewSet)
router.register('getBarUserId', views.getBarUserIdViewSet)
router.register('addBar', views.CreateBarViewSet)
router.register('menuBar', views.MenuBarViewSet)
router.register('menuIncluye', views.MenuIncluyeViewSet)
# Categorias
router.register('categorias', views.CategoriasViewSet)

router.register('editCarta', views.PlatosCategoriasViewSet)
# Valoraciones
router.register('review', views.PlatosValoracionesViewSet)

app_name = 'bares'

urlpatterns = [
    path('',include(router.urls))
]