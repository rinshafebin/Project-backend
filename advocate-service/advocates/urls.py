from django.urls import path
from advocates.views import (
    AdvocateTeamListCreateView,
    AdvocateTeamDetailView,
    AdvocateTeamMemberView,
    CaseListCreateView,
    CaseDetailView,
    CaseAddTeamMemberView,
    CaseDocumentView,
    CaseNotesView,
    AdvocateDashboardView
)

urlpatterns = [
    path('dashboard/', AdvocateDashboardView.as_view(), name='advocate-dashboard'),

    # ---------------- Advocate Team ----------------
    path('teams/', AdvocateTeamListCreateView.as_view(), name='advocate-team-list-create'),
    path('teams/<int:pk>/', AdvocateTeamDetailView.as_view(), name='advocate-team-detail'),
    path('teams/<int:pk>/members/', AdvocateTeamMemberView.as_view(), name='advocate-team-member-manage'),

    # ---------------- Cases ----------------
    path('cases/', CaseListCreateView.as_view(), name='advocate-case-list-create'),
    path('cases/<int:pk>/', CaseDetailView.as_view(), name='advocate-case-detail'),
    path('cases/<int:pk>/add-member/', CaseAddTeamMemberView.as_view(), name='case-add-team-member'),

    # ---------------- Documents & Notes ----------------
    path('cases/<int:case_id>/documents/', CaseDocumentView.as_view(), name='case-documents'),
    path('cases/<int:case_id>/notes/', CaseNotesView.as_view(), name='case-notes'),
]
