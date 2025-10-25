from django.urls import path
from .views import (
    AdvocateCaseListCreateApiView,
    ClientCaseListApiView,
    AdminCaseListAPIView,
    CaseDocumentUploadAPIView,
    CaseDocumentListApiview,
    CaseDocumentDetailAPIView
)

urlpatterns = [
    path('advocate/cases/', AdvocateCaseListCreateApiView.as_view(), name='advocate-cases'),
    path('client/cases/', ClientCaseListApiView.as_view(), name='client-cases'),
    path('admin/cases/', AdminCaseListAPIView.as_view(), name='admin-cases'),
    path('documents/upload/', CaseDocumentUploadAPIView.as_view(), name='document-upload'),
    path('documents/', CaseDocumentListApiview.as_view(), name='document-list'),
    path('documents/case/<int:case_id>/', CaseDocumentListApiview.as_view(), name='document-list-by-case'),
    path('documents/<int:pk>/', CaseDocumentDetailAPIView.as_view(), name='document-detail'),
]
