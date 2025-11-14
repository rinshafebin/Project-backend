# advocates/serializers.py
from rest_framework import serializers
from .models import (
    AdvocateProfile, Specialization, AdvocateTeam, TeamMember, User
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role")


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ("id", "name")


class AdvocateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = SpecializationSerializer(many=True, required=False)

    class Meta:
        model = AdvocateProfile
        fields = [
            "id", "user", "full_name", "phone", "gender", "dob", "bar_council_id",
            "enrollment_year", "experience_years", "languages", "specializations",
            "address_line1", "address_line2", "city", "state", "pincode",
            "profile_image", "is_verified", "rating", "cases_count", "wins_count",
            "created_at", "updated_at"
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


class AdvocateTeamSerializer(serializers.ModelSerializer):
    lead = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = AdvocateTeam
        fields = ("id", "lead", "members", "created_at")


class AdvocateTeamCreateSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)

    class Meta:
        model = AdvocateTeam
        fields = ("id", "lead", "member_ids")

    def create(self, validated_data):
        member_ids = validated_data.pop("member_ids", [])
        lead = validated_data.pop("lead")
        team = AdvocateTeam.objects.create(lead=lead)
        for uid in member_ids:
            try:
                user = User.objects.get(id=uid)
                team.members.add(user)
            except User.DoesNotExist:
                continue
        return team
