"""znl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from news_aggregation import views
from accounts import views as accounts_views #注册
from django.contrib.auth import views as auth_views #用于登录和登出界面

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('news/', views.news, name='news'),
    path('update/', views.update, name='update'),
    path('search/', views.search, name='search'),
    path('home/', views.home, name='home'),
    path('signup', accounts_views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('test/', views.test, name='test'),
    path('profile/', views.profile, name='profile'),
    path('collections/', views.likeNews, name="collections"),
    path('historys/', views.historys, name="historys")

]

