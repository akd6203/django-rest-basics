from poll.models import Question
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework import exceptions
from django.contrib.auth import authenticate
from .models import Profile
# class EmployeeSerializer(serializers.HyperlinkedModelSerializer):

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['salary', 'designation', 'picture']

class EmployeeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id','username', 'first_name',
                'last_name', 'profile', 'email',
                'is_staff', 'is_active', 'date_joined',
                'is_superuser']
                #url

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self,data):
        username = data.get("username","")
        password = data.get("password","")

        if username and password:
            user = authenticate(username=username, password=password) 
            if user:
                if user.is_active:
                    data["user"] = user 
                else:
                    msz = "User is deactivated!."
                    raise exceptions.ValidationError(msz)     
            else:
                msz = "Unable to login with given credentials."
                raise exceptions.ValidationError(msz)
        else:
            msz = "Must provide username and password both."
            raise exceptions.ValidationError(msz)
        return data