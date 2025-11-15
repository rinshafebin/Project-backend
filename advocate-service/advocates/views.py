# advocate_service/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import AdvocateProfile, AdvocateTeam, Specialization
from .serializers import (
    AdvocateProfileSerializer,
    AdvocateTeamSerializer,
    AdvocateTeamCreateSerializer,
    SpecializationSerializer
)
from .permissions import IsAdvocate
from advocate_service.celery import app  # your Celery app


# ------------------------ Helper functions ------------------------
def fetch_user(user_id):
    """Fetch user info from user-service via Celery RPC"""
    try:
        result = app.send_task("user_service.tasks.get_user_info", args=[user_id]).get(timeout=10)
        return result
    except Exception:
        return None


def fetch_case_dashboard(advocate_id):
    """Fetch case dashboard via Celery RPC from case-service"""
    try:
        result = app.send_task("case_service.tasks.get_advocate_dashboard", args=[advocate_id]).get(timeout=15)
        return result
    except Exception:
        return None


# ------------------------ Advocate Profile API ------------------------
class AdvocateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request):
        profile = get_object_or_404(AdvocateProfile, user_id=request.user.id)
        serializer = AdvocateProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = get_object_or_404(AdvocateProfile, user_id=request.user.id)
        serializer = AdvocateProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------ Specialization API ------------------------
class SpecializationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        specs = Specialization.objects.all()
        serializer = SpecializationSerializer(specs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SpecializationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------ Advocate Team APIs ------------------------
class AdvocateTeamListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request):
        teams = AdvocateTeam.objects.filter(lead_id=request.user.id)
        serializer = AdvocateTeamSerializer(teams, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data["lead_id"] = request.user.id
        serializer = AdvocateTeamCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdvocateTeamDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_team(self, pk):
        return get_object_or_404(AdvocateTeam, id=pk, lead_id=self.request.user.id)

    def get(self, request, pk):
        team = self.get_team(pk)
        serializer = AdvocateTeamSerializer(team)
        return Response(serializer.data)

    def put(self, request, pk):
        team = self.get_team(pk)
        serializer = AdvocateTeamCreateSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        team = self.get_team(pk)
        team.delete()
        return Response({"message": "Team deleted"}, status=status.HTTP_204_NO_CONTENT)


# ------------------------ Advocate Dashboard API ------------------------
class AdvocateDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request):
        advocate_id = request.user.id
        dashboard_data = fetch_case_dashboard(advocate_id)

        if dashboard_data is None:
            return Response({"error": "Unable to fetch case dashboard"}, status=502)

        return Response(dashboard_data)
