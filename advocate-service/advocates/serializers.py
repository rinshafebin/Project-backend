from rest_framework import serializers
from .models import (
    Case, CaseDocument, CaseNote,
    AdvocateTeam, CaseTeamMember, User
)

# ------------------------- UserSerializer ---------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


# ------------------------- AdvocateTeamSerializer ---------------------------


class AdvocateTeamSerializer(serializers.ModelSerializer):
    lead = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = AdvocateTeam
        fields = ['id', 'lead', 'members', 'created_at']


# ------------------------- AdvocateTeamCreateSerializer ---------------------------


class AdvocateTeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvocateTeam
        fields = ['id', 'lead', 'members']


# ------------------------- CaseDocumentSerializer ---------------------------

class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = ['id', 'case', 'document', 'uploaded_at', 'visible_to_client', 'visible_to_advocate']


# ------------------------- CaseNoteSerializer ---------------------------

class CaseNoteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = CaseNote
        fields = ['id', 'case', 'note', 'created_by', 'created_at']


# ------------------------- CaseTeamMemberSerializer ---------------------------

class CaseTeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CaseTeamMember
        fields = ['id', 'case', 'user', 'role']

# ------------------------- CaseSerializer ---------------------------

class CaseSerializer(serializers.ModelSerializer):
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
            'client', 'advocate', 'team_members', 'status', 'priority',
            'hearing_date', 'created_at', 'updated_at',
            'documents', 'notes', 'case_team_members'
        ]
