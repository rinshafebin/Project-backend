from rest_framework import serializers
from django.db.models import Q
from .models import (
    Case, CaseDocument, CaseNote,
    AdvocateTeam, CaseTeamMember, User
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class AdvocateTeamSerializer(serializers.ModelSerializer):
    lead = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = AdvocateTeam
        fields = ['id', 'lead', 'members', 'created_at']


class AdvocateTeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvocateTeam
        fields = ['id', 'lead', 'members']


class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = ['id', 'case', 'document', 'uploaded_at', 'visible_to_client', 'visible_to_advocate']


class CaseNoteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = CaseNote
        fields = ['id', 'case', 'note', 'created_by', 'created_at']


class CaseTeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CaseTeamMember
        fields = ['id', 'case', 'user', 'role']


# ✅ FIXED VERSION of CaseSerializer (NO NAME CHANGE)
class CaseSerializer(serializers.ModelSerializer):
    client_identifier = serializers.CharField(write_only=True, required=True)

    # ✅ Mark nested fields as read-only to avoid "Incorrect type" errors
    client = UserSerializer(read_only=True)
    advocate = UserSerializer(read_only=True)
    team_members = UserSerializer(many=True, read_only=True)
    documents = CaseDocumentSerializer(many=True, read_only=True)
    notes = CaseNoteSerializer(many=True, read_only=True)
    case_team_members = CaseTeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Case
        fields = [
            'id', 'title', 'description', 'case_number',
            'client', 'client_identifier', 'advocate', 'team_members',
            'status', 'priority', 'hearing_date', 'created_at', 'updated_at',
            'documents', 'notes', 'case_team_members'
        ]

    def create(self, validated_data):
        # ✅ Handle client_identifier lookup safely
        client_identifier = validated_data.pop('client_identifier')
        try:
            client = User.objects.get(Q(username=client_identifier) | Q(email=client_identifier))
        except User.DoesNotExist:
            raise serializers.ValidationError({'client_identifier': 'Client not found'})

        # ✅ Create the case normally
        case = Case.objects.create(client=client, **validated_data)
        return case
