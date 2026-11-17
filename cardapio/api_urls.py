from django.urls import path

from .api_views import PratoDetail, PratoListCreate

app_name = 'api'
urlpatterns = [
    path('pratos/', PratoListCreate.as_view(), name='prato-list'),
    path('pratos/<int:pk>/', PratoDetail.as_view(), name='prato-detail'),
]
