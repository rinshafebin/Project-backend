from rest_framework import serializers
from clients.models import AdvocateProfile

class AdvocateProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = AdvocateProfile
        fields = [
            'username',
            'email',
            'specialization',
            'office_address',
            'years_of_experience',
            'languages',
        ]
