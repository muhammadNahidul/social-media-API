from django.db import models
from django.conf import settings
from django.utils.text import slugify

from django.utils import timezone
class Profile(models.Model):
    user= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name= models.CharField(max_length=50, null=True, blank=True)
    last_name= models.CharField(max_length=50, null=True, blank=True)

    last_active_at= models.DateTimeField(default=timezone.now, null=True, blank=True)
    profile_img= models.ImageField(upload_to='profile/', blank=True, null= True)
    bio= models.TextField(blank=True, null=True)
    phone= models.CharField(max_length=20, blank=True, null=True)
    address= models.CharField(max_length=200, blank=True, null=True)
    is_private= models.BooleanField(default=False)

    # Social Links
    link1_name = models.CharField(max_length=50, blank=True, null=True)
    link1_url = models.URLField(max_length=255, blank=True, null=True)

    link2_name = models.CharField(max_length=50, blank=True, null=True)
    link2_url = models.URLField(max_length=255, blank=True, null=True)

    link3_name = models.CharField(max_length=50, blank=True, null=True)
    link3_url = models.URLField(max_length=255, blank=True, null=True)

    slug= models.SlugField(unique=True, blank=True)

    def update_last_active(self, update_db=True):
        self.last_active_at= timezone.now()

        if update_db:
            Profile.objects.filter(
                pk= self.pk
            ).update(
                last_active_at= self.last_active_at
            )
    

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug= slugify(f'{self.first_name}-{self.last_name}')
            unique_slug= base_slug
            num= 1

            while Profile.objects.filter(slug= unique_slug).exists():
                unique_slug= f"{base_slug}-{num}"
                num+= 1
                
            self.slug= unique_slug

        super().save(*args, **kwargs)
            
    def __str__(self):
        return f"{self.user.email} Profile"
    

class Follow(models.Model):
    follower= models.ForeignKey(Profile, related_name='following', on_delete=models.CASCADE)
    following= models.ForeignKey(Profile,related_name='followers', on_delete=models.CASCADE)

    created_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together= ('follower', 'following')

    def  __str__(self):
        return f"{self.follower}- {self.following}"


