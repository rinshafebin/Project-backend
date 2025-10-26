from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from advocates.models import Case, CaseDocument, CaseNote
from advocates.serializers import CaseDocumentSerializer, CaseNoteSerializer, CaseSerializer
from advocates.permissions import IsAdvocate, IsClient, IsAdmin


# ------------------ Advocate APIs --------------------

class AdvocateCaseListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request):
        cases = Case.objects.filter(advocate=request.user)
        serializer = CaseSerializer(cases, many=True)
        return Response({
            "success": True,
            "message": f"Found {len(serializer.data)} case(s)",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(advocate=request.user)  
            return Response({
                "success": True,
                "message": "Case created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Case creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



# ------------------ Client APIs --------------------

class ClientCaseListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        cases = Case.objects.filter(client=request.user)
        serializer = CaseSerializer(cases, many=True)
        return Response({
            "success": True,
            "message": f"Found {len(serializer.data)} case(s)",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
        

# ------------------ Admin APIs --------------------


class AdminCaseListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        cases = Case.objects.all()
        serializer = CaseSerializer(cases, many=True)
        return Response({
            "success": True,
            "message": f"Found {len(serializer.data)} case(s)",
            "data": serializer.data
        }, status=status.HTTP_200_OK)



# ------------------ Case document upload --------------------

class CaseDocumentUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CaseDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Document uploaded successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Document upload failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Case documents list --------------------
class CaseDocumentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, case_id=None):
        documents = CaseDocument.objects.all()
        if case_id:
            documents = documents.filter(case__id=case_id)

        user = request.user
        if getattr(user, 'role', None) == "client":
            documents = documents.filter(visible_to_client=True, case__client=user)
        elif getattr(user, 'role', None) == "advocate":
            documents = documents.filter(visible_to_advocate=True, case__advocate=user)

        serializer = CaseDocumentSerializer(documents, many=True)
        return Response({
            "success": True,
            "message": f"Found {len(serializer.data)} document(s)",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

# ------------------ Case document detail --------------------

class CaseDocumentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return CaseDocument.objects.get(pk=pk)
        except CaseDocument.DoesNotExist:
            return None

    def get(self, request, pk):
        document = self.get_object(pk)
        if not document:
            return Response({"success": False, "message": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.role == 'client' and not document.visible_to_client:
            return Response({"success": False, "message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if user.role == 'advocate' and not document.visible_to_advocate:
            return Response({"success": False, "message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CaseDocumentSerializer(document)
        return Response({"success": True, "message": "Document retrieved", "data": serializer.data}, status=status.HTTP_200_OK)


