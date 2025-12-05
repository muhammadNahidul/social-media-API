from django.urls import path

from .views import UserProfiles, UserProfileDetails, ownProfileView, FollowUnfollowView, FollowerList, FollowingList

urlpatterns = [
    path('users/', UserProfiles.as_view()),
    path('users/<slug:slug>/', UserProfileDetails.as_view()),
    path("me/", ownProfileView.as_view(), name=""),
    path('users/follow/<slug:slug>/', FollowUnfollowView.as_view()),
    path('users/follow/<slug:slug>/following/', FollowingList.as_view()),
    path('users/follow/<slug:slug>/followers/', FollowerList.as_view()),

]
