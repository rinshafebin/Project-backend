# advocate_service/serializers.py

from rest_framework import serializers
from .models import AdvocateProfile, AdvocateTeam, Specialization
from advocate_service.celery import app 


# ------------------------ Helper: RPC call to user-service ------------------------

def get_user_rpc(user_id):
    """Fetch user info from user-service via Celery RPC"""
    try:
        result = app.send_task("user_service.tasks.get_user_info", args=[user_id]).get(timeout=10)
        if not result or result.get("id") is None:
            raise serializers.ValidationError(f"User with id {user_id} not found")
        return result
    except Exception as e:
        raise serializers.ValidationError(f"Error fetching user {user_id}: {str(e)}")


# ------------------------ User Serializer ------------------------

class UserSerializer(serializers.Serializer):
    """Populate user from RPC response, not DB"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()


# ------------------------ Specialization Serializer ------------------------

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ("id", "name")


# ------------------------ Advocate Profile Serializer ------------------------


class AdvocateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = SpecializationSerializer(many=True, required=False)

    class Meta:
        model = AdvocateProfile
        fields = [
            "id", "user", "full_name", "phone", "gender", "dob",
            "bar_council_id", "enrollment_year", "experience_years",
            "languages", "specializations", "address_line1", "address_line2",
            "city", "state", "pincode", "profile_image", "is_verified",
            "rating", "cases_count", "wins_count", "created_at", "updated_at"
        ]
        read_only_fields = ("rating", "cases_count", "wins_count", "created_at", "updated_at")

    def create(self, validated_data):
        specs = validated_data.pop("specializations", [])
        profile = AdvocateProfile.objects.create(**validated_data)
        for s in specs:
            obj, _ = Specialization.objects.get_or_create(name=s.get("name"))
            profile.specializations.add(obj)
        return profile

    def update(self, instance, validated_data):
        specs = validated_data.pop("specializations", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if specs is not None:
            instance.specializations.clear()
            for s in specs:
                obj, _ = Specialization.objects.get_or_create(name=s.get("name"))
                instance.specializations.add(obj)
        return instance


# ------------------------ Advocate Team Serializer ------------------------

class AdvocateTeamSerializer(serializers.ModelSerializer):
    lead = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = AdvocateTeam
        fields = ("id", "lead", "members", "created_at")


# ------------------------ Advocate Team Create/Update Serializer ------------------------

class AdvocateTeamCreateSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )
    lead_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AdvocateTeam
        fields = ("id", "lead_id", "member_ids")

    def create(self, validated_data):
        member_ids = validated_data.pop("member_ids", [])
        lead_id = validated_data.pop("lead_id")

        # Fetch lead via RPC
        lead_data = get_user_rpc(lead_id)
        if lead_data["role"] != "advocate":
            raise serializers.ValidationError("Lead must be an advocate")

        team = AdvocateTeam.objects.create(lead_id=lead_id)

        for uid in member_ids:
            user_data = get_user_rpc(uid)
            team.members.add(uid)

        return team

    def update(self, instance, validated_data):
        member_ids = validated_data.pop("member_ids", None)
        lead_id = validated_data.pop("lead_id", None)

        if lead_id:
            lead_data = get_user_rpc(lead_id)
            if lead_data["role"] != "advocate":
                raise serializers.ValidationError("Lead must be an advocate")
            instance.lead_id = lead_id

        instance.save()

        if member_ids is not None:
            instance.members.clear()
            for uid in member_ids:
                user_data = get_user_rpc(uid)
                instance.members.add(uid)

        return instance
