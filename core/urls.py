from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('game/', views.game_view, name='game'),
    path('api/save_score/', views.save_score_api, name='save_score'),
    path('', views.game_view), # Mặc định vào game
]