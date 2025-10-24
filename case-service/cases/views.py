from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cases.models import Case
from cases.serializers import CaseSerializer

class CaseListCreateView(APIView):
    def get(self, request):
        cases = Case.objects.all()
        serializer = CaseSerializer(cases, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CaseDetailView(APIView):
    def get_object(self, pk):
        try:
            return Case.objects.get(pk=pk)
        except Case.DoesNotExist:
            return None

    def get(self, request, pk):
        case = self.get_object(pk)
        if not case:
            return Response({'error': 'Case not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CaseSerializer(case)
        return Response(serializer.data)

    def put(self, request, pk):
        case = self.get_object(pk)
        if not case:
            return Response({'error': 'Case not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CaseSerializer(case, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        case = self.get_object(pk)
        if not case:
            return Response({'error': 'Case not found'}, status=status.HTTP_404_NOT_FOUND)
        case.delete()
        return Response({'message': 'Case deleted'}, status=status.HTTP_204_NO_CONTENT)
