from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("profile", views.profile, name="profile"),
    path("profile/update", views.update_profile, name="update_profile"),
    path("login-required", views.login_required, name="login_required"),
    path("profile/change-password", views.change_password, name="change_password"),
    path("forgot-password", views.forgot_password, name="forgot_password"),
    path("reset-password", views.reset_password, name="reset_password"),
]
