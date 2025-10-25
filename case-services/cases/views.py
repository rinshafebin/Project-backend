from pydoc import doc
from urllib import response
from rest_framework import APIView 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from cases.models import Case, CaseDocument, CaseNote
from cases.serializers import CaseDocumentSerializer,CaseNoteSerializer,CaseSerializer


# -------- Advocate apis for creating and getting cases ----------

class AdvocateCaseListCreateApiView(APIView):
    permission_classes =[IsAuthenticated]
    
    def get(Self,request):
        if request.user.rolec != 'advocate':
            return Response({"detail":"Forbidden"},status=status.HTTP_403_FORBIDDEN)
        cases = Case.objects.filter(advocate=request.user)
        serializer = CaseSerializer(cases,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        if request.user.role != 'advocate':
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        data['advocate'] = request.user.id
        serializer = CaseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Case created successfully",
                "data": serializer.data }, 
                status=status.HTTP_201_CREATED
                )
        return Response({
             "success": False,
            "message": "Case creation failed",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST)


# -----------  clients api for getting the cases ---------------

class ClientCaseListApiView(APIView):
    permission_classes =[IsAuthenticated]
    
    def get(self,request):
        if request.user.role != 'client':
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        cases =Case.objects.filter(client =request.user)
        serializer = CaseSerializer(cases,many=True)
        return Response(
            {
            "success": True,
            "message": f"Found {len(serializer.data)} case(s)",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
        )
    
      
      
# -------------   admin view to cases -----------------

class AdminCaseListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'admin':
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        cases = Case.objects.all()
        serializer = CaseSerializer(cases, many=True)
        return Response(serializer.data)

  
# -------------   case documents -----------------

class CaseDocumentUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        serializer = CaseDocumentSerializer(data = request.data)
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
            
    
# -------------   case documents list -----------------

class CaseDocumentListApiview(APIView):
    permission_classes =[IsAuthenticated]
    
    def get(self,request,case_id=None):
        if case_id:
            documents = CaseDocument.objects.filter(case__id=case_id)
            
        user =request.user
        if user.role =="client":
            documents = documents.filter(visible_to_client=True,case__clients=user)
        elif user.role == "advocate":
            documents = documents.filter(visible_to_advocate=True,case__advocate=user)
            
        serializer = CaseDocumentSerializer(documents, many=True)
        return Response({
            "success": True,
            "message": f"Found {len(serializer.data)} document(s)",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        

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
