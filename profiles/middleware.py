from django.utils import timezone
from .models import Profile


class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response= get_response
    
    def __call__(self, request):
        
        if request.user.is_authenticated:
            try:
                profile= Profile.objects.get(user= request.user)
                profile.last_active_at= timezone.now()

                profile.save(update_fields=['last_active_at'])
            
            except Profile.DoesNotExist:
                pass

        response= self.get_response(request)
        return response
        
class LastActiveMiddleware:
    def __init__(self, get_response):
        self.get_response= get_response

    def __call__(self,request):
        if request.user.is_authenticated:
            try:
                profile= Profile.objects.get(user=request.user)
                profile.update_last_active()
            except Profile.DoesNotExist:
                pass

        response= self.get_response(request)
        return response

