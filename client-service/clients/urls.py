from django.urls import path
from .views import AdvocateSearchView

urlpatterns = [
    path('advocates-search/', AdvocateSearchView.as_view(), name='advocate-search'),
]
