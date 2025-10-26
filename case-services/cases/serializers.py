from rest_framework import serializers
from cases.models import Case,CaseDocument,CaseNote
from django.contrib.auth import get_user_model

User =get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','role']
        


class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = ['id','case','document','uploaded_at','updated_at','visible_to_client','visible_to_advocate']
        


class CaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseNote
        fields = ['id','case','note','created_by','created_at']
        

class CaseSerializer(serializers.ModelSerializer):
    documents = CaseDocumentSerializer(many=True,read_only=True)
    notes = CaseNoteSerializer(many=True,read_only=True)
    client = UserSerializer(read_only=True)
    advocate = UserSerializer(read_only = True)
    
    class Meta:
        model = Case
        fields = [
            'id','title','description','case_number','client','advocate','status',
            'hearing_date','created_at','updated_at','documents','notes'
        ]
        
        