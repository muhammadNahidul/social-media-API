from rest_framework import serializers

from django.utils.timesince import timesince
from .models import Profile, Follow


class ProfileSerializer(serializers.ModelSerializer):
    # profile_img= 
    last_seen_human = serializers.SerializerMethodField()

    class Meta:
        model= Profile
        fields= [
            'slug', 'last_active_at', 'last_seen_human', 'first_name', 'last_name', 'phone', 'address', 'bio','is_private', 'profile_img',
            'link1_name', 'link1_url',
            'link2_name', 'link2_url',
            'link3_name', 'link3_url',
        ]


    
    def validate(self, data):
        pairs= [
            ('link1_name', 'link1_url'),
            ('link2_name', 'link2_url'),
            ('link3_name', 'link3_url'),
        ]

        for name_field, url_field in pairs:
            name= data.get(name_field)
            url= data.get(url_field)

            if url and not name:
                raise serializers.ValidationError({
                    name_field: f"{name_field} is required when {url_field} is provided"
                })
            
            if name and not url:
                raise serializers.ValidationError({
                    url_field: f"{url_field} is required when {name_field} is provided"
                })
            
        return data
    
    def get_last_seen_human(self, obj):
        if obj.last_active_at:
            return timesince(obj.last_active_at) + "ago"
        
        return 'N/A'
    

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model= Follow
        fields= ['id', 'follower', 'following', 'created_at']

        # read_only_fields= ['follower', 'created_at']


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model= Profile
        fields= ['first_name', 'last_name', 'slug']