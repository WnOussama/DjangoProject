from django.urls import path
from . import views
urlpatterns = [
    path('register/',views.registration, name="signup"),
    path('register-details/',views.registration_step2, name="signup_details"),
    path('login/',views.login_page, name="login_page"),
    path('logout/',views.logout_view, name="logout"),

    # demo for user testing and visit my site
    path('demo/login/', views.demo_login, name="demo_login"),

    # Google Auth
    path('google-auth/', views.google_login, name="google_login"),
    path('google/callback/', views.google_callback, name="google_callback"),
]
