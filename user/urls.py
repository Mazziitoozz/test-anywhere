from django.urls import path,include

from user import views
from rest_framework.routers import DefaultRouter
from rest_framework import routers

# Use Viewsets
# router = DefaultRouter()
# router.register('create1/', views.CreateUserViewset)
router = routers.DefaultRouter(trailing_slash=False)
# Reset Password
router.register('newPassword',views.NewPasswordViewSet, basename="resetpasswordstart")
router.register('checkToken',views.CheckTokenViewSet, basename="checkToken")
router.register('resetPassword',views.FinalPasswordViewSet, basename="resetpasswordend")
#Contact Us
router.register('contactUs',views.ContactViewSet, basename="contactUs")

# path('create/',views.CreateUserView.as_view(),name='create'), # the name is useful for reverse function
# path('token/', views.CreateTokenView.as_view(), name='token'),
# path('edit/',views.RetrieveUpdateUserView.as_view(),name='edit'),
# path('delete/',views.DestroyUserView.as_view(),name='delete'),
app_name = 'user'

urlpatterns = [
    path('create/',views.CreateUserView.as_view(),name='create'), # the name is useful for reverse function
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('edit/',views.RetrieveUpdateUserView.as_view(),name='edit'),
    path('delete/',views.DestroyUserView.as_view(),name='delete'),
    path('',include(router.urls))
    
    # path('', include(router.urls))
]