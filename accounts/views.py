from django.shortcuts import render
from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .serializers import LoginSerializer, RegisterSerializer, OTPSerializer
from .models import UserRegisters
from .email import send_otp_email_via

"""Schema"""
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiTypes


# Create your views here.
@extend_schema(
    summary="Register a new user",
    description="Registers a new user and sends an OTP to the email for verification.",
    request=RegisterSerializer,
    responses={
        200: OpenApiResponse(description="OTP sent successfully"),
        400: OpenApiResponse(description="Validation error or user already exists"),
        500: OpenApiResponse(description="Server error")
    },
    examples=[
        OpenApiExample(
            "Register Example",
            value={
                "email": "user@example.com",
                "password": "strongpassword123"
            },
            request_only=True
        )
    ]
)
class RegisterView(APIView):
    def post(self, request):
        try:
            serializer= RegisterSerializer  (data= request.data)
            if serializer.is_valid():

                serializer.save()

                send_otp_email_via(serializer.data['email'])
                return Response({
                    'status': 200,
                    'message': 'please check you email for OTP',
                    'data': serializer.data
                })
            return Response({
                    'status': 400,
                    'message': 'something went wrong',
                    'erros': serializer.errors
            })
        
        except Exception as e:
            return Response({
                    'status': 500,
                    'message': 'something went wrong',
                    'errors': str(e)
            })




@extend_schema(
    summary="Login a user",
    description="Authenticate user using email and password. Returns access and refresh tokens.",
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            description="Login successful",
            examples=[
                OpenApiExample(
                    "Login Success Example",
                    value={
                        "status": 200,
                        "message": "login successful",
                        "user": {"id": 1, "email": "user@example.com"},
                        "access_token": "string",
                        "refresh_token": "string"
                    }
                )
            ]
        ),
        400: OpenApiResponse(description="Validation error"),
        404: OpenApiResponse(description="Email or password incorrect"),
        500: OpenApiResponse(description="Server error")
    }
)
class LoginView(APIView):
    def post(self, request):
        try:
            serializer= LoginSerializer(data= request.data)
            
            if serializer.is_valid():
                email= serializer.validated_data.get('email')
                password= serializer.validated_data.get('password')


                user= authenticate(request, email=email, password=password)

                if user is None:
                    return Response({
                        'status': 404,
                        'message': 'Email or Password Not Correct',
                        'errors': serializer.errors
                    })
                
                if not user.is_verified:
                    return Response({
                        'status': 400,
                        'message': 'your account is not verified. please verified your email'
                    })
                
                refresh_token= RefreshToken.for_user(user)


                return Response({
                    'status': 200,
                    'message': 'login successfull',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                    },
                    'access_token': str(refresh_token.access_token),
                    'refresh_token': str(refresh_token)
                })
            return Response({
                'status': 400,
                'message': 'something went wrong',
                'errors': serializer.errors
            })
            
        except Exception as e:
            return Response({
                'data': 500,
                'message': 'something went wrong',
                'errors': str(e)
            })
        
@extend_schema(
    summary="Verify Email with OTP",
    description="Verify the user's email using the OTP sent to their registered email.",
    request=OTPSerializer,
    responses={
        200: OpenApiResponse(description="Email verified successfully"),
        400: OpenApiResponse(description="Invalid email or wrong OTP"),
        500: OpenApiResponse(description="Server error")
    },
    examples=[
        OpenApiExample(
            "OTP Verification Example",
            value={"email": "user@example.com", "otp": "123456"},
            request_only=True
        )
    ]
)
class EmailVerifyView(APIView):
    def post(self, request):
        try:

            serializer= OTPSerializer(data= request.data)

            if serializer.is_valid():
                email= serializer.validated_data.get('email')
                otp= serializer.validated_data.get('otp')

                user_qs= UserRegisters.objects.filter(email=email)
            
                if not user_qs:
                    return Response({
                        'status':400,
                        'message': 'Invalid Email'
                    })
                
                user= user_qs.first()
                
                if str(user.otp) != str(otp):
                    return Response({
                        'status': 400,
                        'message': 'wrong otp'
                    })
                
                user.is_verified= True
                user.save()

                return Response({
                    'status': 200,
                    'message': 'email verify successfully!'
                })
            return Response({
                'status': 400,
                'message': 'something wrong'
            })

        except Exception as e:
            print(e)
            return Response({
                'status': 500,
                'message': 'Something went wrong',
                'error': str(e)
            })
        

@extend_schema(
    summary="Refresh JWT Access Token",
    description="Generate a new access token using the refresh token.",
    request=OpenApiTypes.OBJECT,
    parameters=[
        OpenApiParameter(name="refresh_token", type=str, description="Refresh token in request body or header 'refresh-token'")
    ],
    responses={
        200: OpenApiResponse(description="New access token generated"),
        400: OpenApiResponse(description="Refresh token is required"),
        402: OpenApiResponse(description="Invalid refresh token"),
        500: OpenApiResponse(description="Server error")
    },
    examples=[
        OpenApiExample(
            "Refresh Token Example",
            value={"refresh_token": "string"},
            request_only=True
        )
    ]
)
class CustomRefreshTokenView(APIView):
    def post(self, request):
        try:
            body_token= request.data.get('refresh_token')
            header_token= request.headers.get('refresh-token')

            refresh_token= body_token or header_token

            if refresh_token is None:
                return Response({
                    'status': 400,
                    'message': 'Refresh Token is required!'
                })
        
         
            try:
                refresh= RefreshToken(refresh_token)

            except TokenError:
                return Response({
                    'status': 402,
                    'message': 'Invalid refresh token'
                })
            
            new_access_token= refresh.access_token

            return Response({
                'status': 200,
                'message': 'New Access Token generated',
                'access_token': str(new_access_token)
            })
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'something went wrong!',
                'errors': str(e)
            })
    
