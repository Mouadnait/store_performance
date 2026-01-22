"""
URL configuration for performance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import register, login_view, logout_view

urlpatterns = [
    path('', login_view, name="login"),
    path('', login_view, name="sign-in"),  # compatibility alias
    path('signup/', register, name="signup"),
    path('sign-up/', register, name="sign-up"),  # compatibility alias
    path('logout/', logout_view, name="logout"),
    path('sign-out/', logout_view, name="sign-out"),  # compatibility alias
    path('home/', login_view, name="home"),  # Home redirects to login if not authenticated
]
