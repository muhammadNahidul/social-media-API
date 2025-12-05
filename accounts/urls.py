from django.urls import path 


from .views import RegisterView, LoginView, EmailVerifyView, CustomRefreshTokenView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('verify/', EmailVerifyView.as_view()),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='custom_refresh'),

]
