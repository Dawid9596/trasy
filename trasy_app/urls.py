from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .api_views import ObrazTlaViewSet, TrasaViewSet, PunktTrasyViewSet

router = DefaultRouter()
router.register(r'obrazy-tla', ObrazTlaViewSet)
router.register(r'trasy', TrasaViewSet, basename='trasa')

api_urlpatterns = [
    path('', include(router.urls)),
    path('token-auth/', obtain_auth_token, name='api_token_auth'),
    path('trasy/<int:trasa_id>/punkty/', PunktTrasyViewSet.as_view({'get': 'list', 'post': 'create'}), name='punkty-list'),
    path('trasy/<int:trasa_id>/punkty/<int:pk>/', PunktTrasyViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='punkt-detail'),
]

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='trasy_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='trasy_app/logout.html'), name='logout'),
    path('tla/', views.tlo_list, name='tlo_list'),
    path('trasa/create/<int:tlo_id>/', views.trasa_create, name='trasa_create'),
    path('trasa/edit/<int:trasa_id>/', views.trasa_edit, name='trasa_edit'),
    path('punkt/delete/<int:punkt_id>/', views.punkt_delete, name='punkt_delete'),
    path('moje-trasy/', views.user_trasy, name='user_trasy'),
    path('trasa/<int:trasa_id>/add-point-click/', views.add_point_click, name='add_point_click'),
    path('punkt/move/<int:punkt_id>/<str:kierunek>/', views.punkt_move, name='punkt_move'),
    path('trasa/<int:trasa_id>/punkty/', views.get_punkty, name='get_punkty'),
    
    # API URL-e
    path('api/', include(api_urlpatterns)),
    path('api-auth/', include('rest_framework.urls')),
]