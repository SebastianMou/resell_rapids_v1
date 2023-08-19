from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='user_login'),
    path('login_with_email/', views.login_with_email, name='login_with_email'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.user_register, name='user_register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('profile/', views.profile, name='profile'),

    path('tasks/', views.tasks, name='tasks'),
    path('items/', views.update_task_order, name='update_task_order'),
    path('items_detail/<int:pk>/', views.items_detail, name='items_detail'),
    path('create_task/', views.create_task, name='create_task'),

    path('settings/', views.settings, name='settings'),
    path('terms_of_service/', views.terms_of_service, name='terms_of_service'),
    path('email_service/', views.email_service, name='email_service'),
    
    path('a_analytics/', views.a_analytics, name='a_analytics'),
    path('tables/', views.tables, name='tables'),

    # Forgoten password
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), name="password_reset"),
    path('password_reset_sent/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="authentication/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),

    # activación de la cuenta de usuario por correo electrónico
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('sending_activate_token/', views.sending_activate_token, name='sending_activate_token'), 
]