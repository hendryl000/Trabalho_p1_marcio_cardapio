from django.urls import path
from .dashboard_views import dashboard_api

from .api_views import PratoDetail, PratoListCreate

app_name = 'api'
urlpatterns = [
    path('dashboard/', dashboard_api, name='dashboard'),
    path('pratos/', PratoListCreate.as_view(), name='prato-list'),
    path('pratos/<int:pk>/', PratoDetail.as_view(), name='prato-detail'),
]
