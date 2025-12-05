from rest_framework import serializers

from django.contrib.auth import authenticate

from .models import UserRegisters

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model= UserRegisters
        fields= ['email', 'password']

    def create(self, validated_data):
        email= validated_data.get('email')
        password= validated_data.get('password')

        user= UserRegisters.objects.create_user(email=email, password=password)

        
        return user 
    
class LoginSerializer(serializers.Serializer):
    email= serializers.EmailField(required= True)
    password= serializers.CharField(write_only= True, required= True)

    def validate(self, data):
        email= data.get('email')
        password= data.get('password')

        user= authenticate(email=email, password=password)


        if not user:
            raise serializers.ValidationError("email or password not correct")
        data['user']= user
        return data
    

class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required= True)
    otp= serializers.CharField(max_length= 6, required= True)
    
