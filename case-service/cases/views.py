from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Case, CaseTeamMember, CaseDocument, CaseNote
from .serializers import (
    CaseSerializer,
    CaseTeamMemberSerializer,
    CaseDocumentSerializer,
    CaseNoteSerializer
)



class CaseListCreateView(APIView):
    def get(self, request):
        cases = Case.objects.all().order_by('-created_at')
        serializer = CaseSerializer(cases, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CaseDetailView(APIView):
    def get(self, request, case_id):
        try:
            case = Case.objects.get(pk=case_id)
        except Case.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CaseSerializer(case)
        return Response(serializer.data)

    def put(self, request, case_id):
        try:
            case = Case.objects.get(pk=case_id)
        except Case.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CaseSerializer(case, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, case_id):
        try:
            case = Case.objects.get(pk=case_id)
        except Case.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        case.delete()
        return Response({"message": "Case deleted!"}, status=status.HTTP_204_NO_CONTENT)




class AddCaseTeamMemberView(APIView):
    def post(self, request):
        serializer = CaseTeamMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Team member added", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveCaseTeamMemberView(APIView):
    def delete(self, request):
        case_id = request.data.get("case")
        user_id = request.data.get("user_id")

        try:
            member = CaseTeamMember.objects.get(case_id=case_id, user_id=user_id)
        except CaseTeamMember.DoesNotExist:
            return Response({"error": "Team member not found"}, status=status.HTTP_404_NOT_FOUND)

        member.delete()
        return Response({"message": "Team member removed"})



class UploadCaseDocumentView(APIView):
    def post(self, request):
        serializer = CaseDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Document uploaded", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CaseDocumentsView(APIView):
    def get(self, request, case_id):
        docs = CaseDocument.objects.filter(case_id=case_id)
        serializer = CaseDocumentSerializer(docs, many=True)
        return Response(serializer.data)



class AddCaseNoteView(APIView):
    def post(self, request):
        serializer = CaseNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Note added", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CaseNotesView(APIView):
    def get(self, request, case_id):
        notes = CaseNote.objects.filter(case_id=case_id)
        serializer = CaseNoteSerializer(notes, many=True)
        return Response(serializer.data)




class CaseFullDetailView(APIView):
    def get(self, request, case_id):
        try:
            case = Case.objects.get(id=case_id)
        except Case.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        case_data = CaseSerializer(case).data
        case_data["team_members"] = CaseTeamMemberSerializer(case.case_team_members.all(), many=True).data
        case_data["documents"] = CaseDocumentSerializer(case.documents.all(), many=True).data
        case_data["notes"] = CaseNoteSerializer(case.notes.all(), many=True).data

        return Response(case_data)
