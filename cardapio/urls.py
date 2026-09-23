from django.urls import path
from . import views
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('cardapio/', views.menu, name='menu'),
    path('mesas/<int:pk>/abrir/', views.abrir, name='abrir'),
    path('comandas/<int:pk>/', views.comanda, name='comanda'),
    path('comandas/<int:pk>/fechar/', views.fechar, name='fechar'),
    path('comandas/<int:pk>/itens/<int:item_pk>/remover/', views.remover_item, name='remover_item'),
    path('historico/', views.historico, name='historico'),
    path('cadastros/<str:tipo>/', views.cadastro, name='cadastro'),
    path('cadastros/<str:tipo>/<int:pk>/', views.cadastro, name='editar'),
    path('cadastros/<str:tipo>/<int:pk>/excluir/', views.excluir, name='excluir'),
]
