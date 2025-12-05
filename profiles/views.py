from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Profile, Follow
from .serializers import ProfileSerializer, FollowSerializer, SimpleUserSerializer

from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.auth import get_user_model

"""Schema"""
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiTypes


# Create your views here.

@extend_schema(
    summary= 'Get All User Profiles',
    description= "Returns a list of all user profiles",
    responses=ProfileSerializer(many=True)
)
class UserProfiles(APIView):

    permission_classes= [IsAuthenticated]
    authentication_classes= [JWTAuthentication]

    def get(self, request):
        profile= Profile.objects.all()
        serializer= ProfileSerializer(profile, many=True)

        return Response(serializer.data)
    

    @extend_schema(
        summary= "Create Your Profile",
        description= "Creates profile for logged-in user. A user can create only one profile.",
        request= ProfileSerializer,
        responses={
            201: ProfileSerializer,
            400: OpenApiResponse(description="Profile already exists or validation error"),
        }
    )
    def post(self, request):
        try:
            if Profile.objects.filter(user= request.user).exists():
                return Response({
                    'status': 400,
                    'message': 'Profile Already Created!'
                })
            serializer= ProfileSerializer(data= request.data)
            if serializer.is_valid():
                serializer.save(user= request.user)
                return Response({
                    'status': 201,
                    'message': "Profile Created Successfully",
                    'data': serializer.data
                })
            
            return Response({
                'status': 400,
                'message': 'something went wrong',
                'errors': serializer.errors
            })
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'something went wrong'
            })
        
@extend_schema(
    summary="Get a Single User Profile",
    description="Retrieve a user's profile using slug. If profile is private, only the owner can view.",
    parameters=[OpenApiParameter("slug", str, description="Profile slug")],
    responses={
        200: ProfileSerializer,
        403: OpenApiResponse(description="Profile is private"),
        404: OpenApiResponse(description="Profile not found")
    }
)
class UserProfileDetails(APIView):
    permission_classes= [IsAuthenticated]
    authentication_classes= [JWTAuthentication]
    def get(self, request, slug):
        try:
            profile= get_object_or_404(Profile, slug=slug)

            if profile.is_private and profile.user != request.user:
                return Response({
                    'status': 403,
                    'message': 'This Profile is Private'
                })
            
            serializer= ProfileSerializer(profile)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                    'status': 500,
                    'message': "something went wrong",
                    'errors': str(e)
            })
    @extend_schema(
            summary= "Update User Profile",
            description= "Update a user's Profile using slug. Only partial update allowed.",
            request= ProfileSerializer,
            parameters=[OpenApiParameter('slug', str)],
            responses={
                200: ProfileSerializer,
                400: OpenApiResponse(description="Invalid data"),
                404: OpenApiResponse(description="Profile not Found")
            }
    )
    def put(self, request, slug):
        try:
            profile= get_object_or_404(Profile, slug=slug)
            serializer = ProfileSerializer(profile, data= request.data, partial= True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 200,
                    'message': 'Profile updated successfully',
                    'data': serializer.data
                })
            
            return Response({
                'status': 400,
                'message': 'invalid data',
                'errors': serializer.errors
            })
    
        except Exception as e:
            return Response({
                    'status': 500,
                    'message': "something went wrong",
                    'errors': str(e)
            })
        

class UpdateSocialLinks(APIView):
    permission_classes= [IsAuthenticated]
    authentication_classes= [JWTAuthentication]


    @extend_schema(
        summary="Update social links",
        description="Update link1, link2, link3 name and URL fields.",
        request=OpenApiTypes.OBJECT,  # Incoming JSON Body
        responses={
            200: OpenApiResponse(
                description="Social Links Updated Successfully",
            ),
            400: OpenApiResponse(
                description="Validation Error"
            ),
        },
        examples=[
            OpenApiExample(
                "Update Social Links Example",
                value={
                    "link1_name": "Facebook",
                    "link1_url": "https://facebook.com/username",
                    "link2_name": "Instagram",
                    "link2_url": "https://instagram.com/username",
                    "link3_name": "LinkedIn",
                    "link3_url": "https://linkedin.com/in/username",
                },
                request_only=True,
            )
        ]
    )
    def put(self, request):
        profile= Profile.objects.get(user= request.user)

        allowed_fields= [
            'link1_name', 'link1_url',
            'link2_name', 'link2_url',
            'link3_name', 'link3_url',
        ]

        incoming_data= {k: v for k, v in request.data.items() if k in allowed_fields}

        serializer= ProfileSerializer(profile, data= incoming_data, partial= True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 200,
                'message': 'Social Links updated',
                'data': serializer.data
            })
        return Response({
                'status': 400,
                'message': 'somethign went wrong',
                'errors': serializer.errors  
            })
    

@extend_schema(
    summary="Get or Update Own Profile",
    description="Retrieve or update the profile of the currently logged-in user.",
    responses={
        200: ProfileSerializer,
        400: OpenApiResponse(description="Validation error"),
        404: OpenApiResponse(description="Profile not found"),
        500: OpenApiResponse(description="Internal server error")
    },
    examples=[
        OpenApiExample(
            name="Update Own Profile Example",
            value={
                "first_name": "Nahidul",
                "last_name": "Islam",
                "bio": "I love coding!",
                "phone": "+880123456789",
                "address": "Dhaka, Bangladesh",
                "link1_name": "Facebook",
                "link1_url": "https://facebook.com/username",
            },
            request_only=True
        )
    ]
)
class ownProfileView(APIView):

    permission_classes= [IsAuthenticated]
    authentication_classes= [JWTAuthentication]

    def get(self, request):
        try:
            profile= get_object_or_404(Profile, user= request.user)
            serializer= ProfileSerializer(profile)

            return Response({
                'status': 200,
                'message': 'Profile fetched successfully',
                'data': serializer.data
            })
        
        except Exception as e:
            return Response({
                'status': 500,
                'message': "something went wrong",
                'errors': str(e)
            })
        
    def put(self, request):
        try: 
            profile= get_object_or_404(Profile, user= request.user)
            serializer= ProfileSerializer(profile, data=request.data, partial= True)

            if serializer.is_valid():
                serializer.save()

                return Response({
                    'status': 200,
                    'message': 'Your Profile Updated successfully',
                    'data': serializer.data
                })
            return Response({
                'status': 400,
                'message': 'somethign went wrong',
                'errors': serializer.errors  
            })
        
        except Exception as e:
            return Response({
                'status': 500,
                'message': "something went wrong",
                'errors': str(e)
            })
        



""" follow unfollow  """
@extend_schema(
    summary="Follow or Unfollow a user",
    description="Follow a user by their profile slug. If already following, it will unfollow.",
    parameters=[OpenApiParameter(name="slug", type=str, description="Target user profile slug", required=True)],
    request=OpenApiTypes.NONE,  # POST body is empty
    responses={
        200: OpenApiResponse(
            description="Successfully followed or unfollowed",
            examples=[
                OpenApiExample(
                    name="Follow Example",
                    value={
                        "message": "Followed Successfully",
                        "data": {
                            "follower": "nahidul",
                            "following": "username",
                            "id": 5
                        }
                    },
                ),
                OpenApiExample(
                    name="Unfollow Example",
                    value={"message": "Unfollow successfully"}
                )
            ]
        ),
        400: OpenApiResponse(description="Cannot follow yourself"),
        404: OpenApiResponse(description="Target profile not found"),
    }
)
class FollowUnfollowView(APIView):
    permission_classes= [IsAuthenticated]
    authentication_classes= [JWTAuthentication]
    def post(self, request, slug):
        my_profile= get_object_or_404(Profile, user=request.user)
        target_user= get_object_or_404(Profile, slug= slug)

        if target_user == my_profile:
            return Response({
                'message': "You  can't follow your account"
            }, status=400)

        follow_exists= Follow.objects.filter(
            follower= my_profile,
            following= target_user
        ).first()

        if follow_exists:
            follow_exists.delete() #unfollow
            return Response({
                'message': 'Unfollow successfully'
            })
        
        follow= Follow.objects.create(
            follower= my_profile,
            following= target_user
        )

        return Response({
            'message': 'Followed Successfully',
            'data': FollowSerializer(follow).data
        })
    

@extend_schema(
    summary="Get Followers of a User",
    description="Retrieve a list of users who are following the given profile.",
    parameters=[
        OpenApiParameter("slug", str, description="Profile slug of the target user", required=True)
    ],
    responses=SimpleUserSerializer(many=True)
)
class FollowerList(APIView):
    permission_classes= [IsAuthenticated]
    authentication_classes= [JWTAuthentication]
    
    def get(self, request, slug):
        profile= get_object_or_404(Profile, slug=slug)

        followers= Follow.objects.filter(following= profile).select_related('follower')
        follower_profile= [f.follower for f in followers]

        serializer= SimpleUserSerializer(follower_profile, many= True)
        return Response(serializer.data)

@extend_schema(
    summary="Get Following of a User",
    description="Retrieve a list of users whom the given profile is following.",
    parameters=[
        OpenApiParameter("slug", str, description="Profile slug of the target user", required=True)
    ],
    responses=SimpleUserSerializer(many=True)
)
class FollowingList(APIView):
    permission_classes= [IsAuthenticated]
    authentication_classes= [JWTAuthentication]
    
    def get(self, request, slug):
        profile= get_object_or_404(Profile, slug=slug)

        following= Follow.objects.filter(follower= profile).select_related('following')

        following_profile= [f.following for f in following]

        serializer= SimpleUserSerializer(following_profile, many=True)

        return Response(serializer.data)



