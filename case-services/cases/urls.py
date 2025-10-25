from django.urls import path
from .views import (
    AdvocateCaseListCreateAPIView,
    ClientCaseListAPIView,
    AdminCaseListAPIView,
    CaseDocumentUploadAPIView,
    CaseDocumentListAPIView,
    CaseDocumentDetailAPIView,
)

urlpatterns = [
    # Advocate endpoints
    path('advocate/', AdvocateCaseListCreateAPIView.as_view(), name='advocate-case-list-create'),

    # Client endpoints
    path('client/', ClientCaseListAPIView.as_view(), name='client-case-list'),

    # Admin endpoints
    path('admin/', AdminCaseListAPIView.as_view(), name='admin-case-list'),

    # Case document endpoints
    path('documents/upload/', CaseDocumentUploadAPIView.as_view(), name='case-document-upload'),
    path('documents/', CaseDocumentListAPIView.as_view(), name='case-document-list'),
    path('documents/<int:case_id>/', CaseDocumentListAPIView.as_view(), name='case-document-list-by-case'),
    path('documents/detail/<int:pk>/', CaseDocumentDetailAPIView.as_view(), name='case-document-detail'),
]
