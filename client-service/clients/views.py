from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import AdvocateProfile
from .serializers import AdvocateProfileSerializer

class AdvocateSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('query', '')
        advocates = AdvocateProfile.objects.filter(
            Q(user__role='advocate') &
            (
                Q(user__username__icontains=query) |
                Q(specialization__icontains=query) |
                Q(office_address__icontains=query) |
                Q(languages__icontains=query)
            )
        )

        serializer = AdvocateProfileSerializer(advocates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
