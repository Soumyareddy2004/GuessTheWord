from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('start/', views.start_game, name='start_game'),
    path('play/<int:game_id>/', views.play_game, name='play'),
    path('report/day/', views.report_day, name='report_day'),
    path('report/user/', views.report_user, name='report_user'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # optional
]
