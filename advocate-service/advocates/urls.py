# urls.py
from django.urls import path
from .views import (
    AdvocateProfileAPIView,
    SpecializationAPIView,
    AdvocateTeamListCreateAPIView,
    AdvocateTeamDetailAPIView,
    AdvocateDashboardAPIView,
)

urlpatterns = [
    path('profile/', AdvocateProfileAPIView.as_view(), name='advocate-profile'),
    path('specializations/', SpecializationAPIView.as_view(), name='specializations'),
    path('teams/', AdvocateTeamListCreateAPIView.as_view(), name='advocate-teams'),
    path('teams/<int:pk>/', AdvocateTeamDetailAPIView.as_view(), name='advocate-team-detail'),
    path('dashboard/', AdvocateDashboardAPIView.as_view(), name='advocate-dashboard'),
]
