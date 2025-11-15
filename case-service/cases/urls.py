from django.urls import path
from .views import (
    CaseListCreateView,
    CaseDetailView,
    AddCaseTeamMemberView,
    RemoveCaseTeamMemberView,
    UploadCaseDocumentView,
    CaseDocumentsView,
    AddCaseNoteView,
    CaseNotesView,
    CaseFullDetailView
)

urlpatterns = [
    path('cases/', CaseListCreateView.as_view(), name='case-list-create'),
    path('cases/<int:case_id>/', CaseDetailView.as_view(), name='case-detail'),

    path('cases/<int:case_id>/full/', CaseFullDetailView.as_view(), name='case-full-detail'),

    path('cases/team/add/', AddCaseTeamMemberView.as_view(), name='case-team-add'),
    path('cases/team/remove/', RemoveCaseTeamMemberView.as_view(), name='case-team-remove'),

    path('cases/<int:case_id>/documents/', CaseDocumentsView.as_view(), name='case-documents'),
    path('cases/documents/upload/', UploadCaseDocumentView.as_view(), name='case-document-upload'),

    path('cases/<int:case_id>/notes/', CaseNotesView.as_view(), name='case-notes'),
    path('cases/notes/add/', AddCaseNoteView.as_view(), name='case-note-add'),
]
