"""
URL configuration for filmexplorer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from films.views import film_base, film_browse, film_details, film_list, film_list_template, films05_list, login_view, logout_view, signup, welcome

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', welcome, name='welcome'),
    path('films01/', film_list, name='film_list'),
    path('films/', film_list_template, name='film_list_template'),
    path('films03/', film_base, name='film_base'),
    path('films_browse/', film_browse, name='film_browse'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup, name='signup'),
    path('films/<str:title>/', film_details, name='film_details'),
    path('films05/', films05_list, name='films05_list'),
]
