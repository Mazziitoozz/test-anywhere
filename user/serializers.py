from rest_framework import serializers, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model,authenticate
from django.utils.translation import ugettext_lazy as _

import re
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users"""
    #is_owner = serializers.HiddenField(default=False)
    class Meta:
        model = get_user_model()
        fields = ("username","email","password","is_owner") # I dont know if we need the bar license. But we need smthg to identify the owner of the
        extra_kwargs = {'password':{'write_only':True,'min_length':5}}
    


    def create(self,validated_data):
        '''create a new user with encrypted password and return it'''
        # We could have used also perform_create in the views instead in the serializer butif you have in the serializer
        # you have the possibility to change the data like the email : https://stackoverflow.com/questions/41094013/when-to-use-serializers-create-and-modelviewsets-create-perform-create
        print(validated_data)
        try:
            return get_user_model().objects.create_user(**validated_data)
        except:
            msg = _('Username already exists')
            raise serializers.ValidationError(msg, code='authorization')

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)  # Check if the user sends the password
        user = super().update(instance, validated_data)
        print(instance,validated_data)
        if password:
            user.set_password(password)
            user.save()
        instance.save()
        return user

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},  # hide the password when you type
        trim_whitespace=False       
    )
    # Remove extra spaces and convert to Uppercase
    # def validate_username(self,value):
    #     upperName = re.sub(' +', ' ',value.upper())        
    #     return upperName

    def validate(self, attrs):
        """Validate and authenticate the user"""
        # Save the attr info in variables
        username = attrs.get('username')
        password = attrs.get('password')
        # Define the user
        # I DONT KNOW IF UNIVERSITIES SHOULD IDENTIFY ALSO WITH THE EMAIL
        user = authenticate(
            request=self.context.get('request'),
            username=username,                      #If we decide that the user only use the email we should change username=email and in the model the USERNAME_FIELD=email
            password=password
        )
       
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user        # we add to attrs a field call user with the username
        return attrs