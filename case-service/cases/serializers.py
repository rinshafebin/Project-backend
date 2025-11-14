from rest_framework import serializers
from .models import Case, CaseTeamMember, CaseDocument, CaseNote


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            'id', 'title', 'description', 'case_number',
            'client_id', 'advocate_id', 'team_id',
            'status', 'result', 'priority',
            'hearing_date',
            'created_at', 'updated_at'
        ]


class CaseTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseTeamMember
        fields = ['id', 'case', 'user_id', 'role']


class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = [
            'id', 'case', 'document', 'uploaded_at',
            'updated_at', 'visible_to_client', 'visible_to_advocate'
        ]


class CaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseNote
        fields = ['id', 'case', 'note', 'created_by_id', 'created_at']
