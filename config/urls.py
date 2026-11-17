from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path('entrar/', auth_views.LoginView.as_view(template_name='cardapio/login.html'), name='login'),
    path('sair/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
    path('api/', include('cardapio.api_urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('cardapio.urls')),
]
