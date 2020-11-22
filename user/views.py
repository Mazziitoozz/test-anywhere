from rest_framework import generics,authentication,permissions,status,exceptions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import viewsets,permissions
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from core.models import User,Bares
from user.serializers import UserSerializer,AuthTokenSerializer
import datetime
import pytz 


class MyAuthentication(authentication.TokenAuthentication):
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
        #The user has 2 hours and after it he needs to refresh
        if token.created < utc_now - datetime.timedelta(hours=2):
            raise exceptions.AuthenticationFailed('Token has expired')
        
        return (token.user, token)

class BaseUserView(generics.GenericAPIView):
    """"Here we should put which is common to the following views like permissions and the object"""
    permissions_classes = (permissions.IsAuthenticated,)
    authentication_classes = (MyAuthentication,)
    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve and return auth user"""
        return self.request.user


# It safer have just a call to Create user. Another different to retrieveUpdate and another one to delete.
class RetrieveUpdateUserView(BaseUserView,generics.RetrieveUpdateAPIView):
    """Update the user info"""

    def update(self, request, *args, **kwargs):
      
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if ((Bares.objects.all().filter(id=self.request.user.id)) and request.data['is_owner'] ==False):
            return Response(data="Tienes un bar asignado",status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

  
    # permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (authentication.TokenAuthentication,)
    # serializer_class = UserSerializer
    # queryset = User.objects.all()
    # lookup_field = 'username'
    # def get_object(self):
    #     username = self.request.user.username
    #     return get_object_or_404(User, username=username)

class DestroyUserView(BaseUserView,generics.DestroyAPIView): # Maybe it is not necessary that the user could delete itself(?), now i will leave just for testing
    """Delete the user"""

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    queryset = User.objects.all()       # I need to add queryset because of the exception in the create method in the serializer. If i catch the error in the view, probably I would not need it


# TOKEN 
class MyRefreshToken(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token, created =  Token.objects.get_or_create(user=serializer.validated_data['user']) # created specify if a new object has been created
            is_owner = User.objects.filter(id=serializer.validated_data['user'].id).values('is_owner')[0]['is_owner']
            # If the owner has already a bar we get it
            if (Bares.objects.all().filter(user_id=token.user_id)):
                bar_id = Bares.objects.all().filter(user_id=token.user_id).values('id')[0]['id']
            else:
                bar_id= False
            if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.datetime.utcnow()
                token.save()
            return Response({'token': token.key, 'is_owner': is_owner,'user_id':token.user_id, 'bar_id': bar_id})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateTokenView(MyRefreshToken):
    """Create a new auth token for the user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

# Send email with the link to change the password. The token must be inside
class NewPasswordViewSet(viewsets.ModelViewSet,MyRefreshToken):
    
    permission_classes = [permissions.AllowAny]

    def create(self, request, pk=None):
        hostname= request.META['HTTP_ORIGIN']                 # Get info where the user is calling localhost,internet...    
        email = request.data['email']                       # Get email adress
        user = User.objects.filter(email=email).values('id')
        if (user):
            user_id = user[0]['id']
            # Get token object
            token = Token.objects.get(user_id=user_id)
            # Generate new Key
            new_key = token.generate_key()
            # Update the token info
            token = Token.objects.filter(user_id=user_id).update(key=new_key)
            token = Token.objects.filter(user_id=user_id).update(created=datetime.datetime.utcnow())

            # Email
            email = EmailMessage(
                        'Reset Password',
                        'Aquí está tu link para recuperar la contraseña: ' + hostname+'/forgotten/'+new_key,
                        'robmafer@hotmail.com',
                        [email],
                        )
            email.send( fail_silently=False)        # Catch errors
            return Response('Email sent')
        else:
            return Response("This e-mail does not exist!")


# The frontend needs get the info of the user who is going to change the password in order to send it back the new password and the email of the user.
class CheckTokenViewSet(viewsets.ModelViewSet):
   # Authentication with token
    permissions_classes = (permissions.IsAuthenticated,)
    authentication_classes = (MyAuthentication,)
    def list(self, request, pk=None): 
        tokenHeader= request.META['HTTP_AUTHORIZATION']     # Get token from header tokenHeader= Bearer eyJ0...
        tokenHeader = tokenHeader[7:]                       # Remove word Bearer in order to get just the token. If you want try in localhost you must set [6:] because instead bearer it appears token
        try:
            # Get user info
            user_id = Token.objects.filter(key=tokenHeader).values('user_id')[0]['user_id']
            email = User.objects.filter(id=user_id).values('email')[0]['email']
            return Response(email)
        except:
            return Response('Something was wrong')

class FinalPasswordViewSet(viewsets.ModelViewSet):
    # Authentication with token
    permissions_classes = (permissions.IsAuthenticated,)
    authentication_classes = (MyAuthentication,)
    # Change password in db
    def create(self, request, pk=None): 
        tokenHeader= request.META['HTTP_AUTHORIZATION']     # Get token from header tokenHeader= Bearer eyJ0...
        tokenHeader = tokenHeader[7:]                       # Remove word token in order to get just the token
        # Catch errors
        try:
            email = request.data['email']                   # Get user email
            password = request.data['password']             # Get password         
            user= User.objects.get(email=email)             # Get user
            user.set_password(password)                     # encrypt password
            user.save()
            return Response('Password changed')
        except:
            return Response('Somtehing was wrong!')

# Contact us
class ContactViewSet(viewsets.ModelViewSet,MyRefreshToken):
    
    permission_classes = [permissions.AllowAny]

    def create(self, request, pk=None): 
        name = request.data['name']                               # Get name 
        email = request.data['email']                             # Get email adress
        phone = request.data['phone']                             # Get phone . could be empty
        subject = request.data['subject']                         # Get subject 
        message = request.data['message']                         # Get message 

        try:
            if phone:   
                # Email
                email = EmailMessage(
                            subject,
                            'Don/doña ' +name+' con email '+email+' y numero de telefono '+ str(phone) +' tiene una consulta relacionada con '+subject+': '+ message,
                            'robmafer@hotmail.com',
                            ['mazziitoozz@gmail.com'],
                            
                            )
            else:
                email = EmailMessage(
                            subject,
                            'Don/doña ' +name+' con email '+email+' tiene una consulta relacionada con '+subject+': '+ message,
                            'robmafer@hotmail.com',
                            ['mazziitoozz@gmail.com'],
                            )
            email.send( fail_silently=False)        # Catch errors
            return Response('Email sent')
        except:
            return Response("Something was wrong")
    

