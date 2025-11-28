from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    # Trang admin
    path('admin/', admin.site.urls),

    # Trang đăng ký
    path('register/', views.register_view, name='register'),
    
    # Trang đăng nhập (dùng view có sẵn của Django)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    # Trang đăng xuất
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Trang chứa game
    path('game/', views.game_view, name='game'),
    
    # API để game gửi điểm về
    path('api/save_score/', views.save_score_api, name='save_score'),
    
    # Mặc định vào game (nếu chưa login sẽ bị đẩy về login)
    path('', views.game_view), 
]