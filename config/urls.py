"""
URL configuration for config project.

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
from core.views import (
    UserListView, UserDetailView,
    ProfileView,
    SongListView, SongDetailView,
    ShareLinkListView, ShareLinkDetailView,
    GoogleLoginView, GoogleCallbackView,
    SunoCallbackView,
)

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('auth/google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/profile/', ProfileView.as_view(), name='user-profile'),
    path('users/<int:user_id>/songs/', SongListView.as_view(), name='song-list'),
    path('users/<int:user_id>/songs/<int:song_id>/', SongDetailView.as_view(), name='song-detail'),
    path('users/<int:user_id>/songs/<int:song_id>/share-links/', ShareLinkListView.as_view(), name='share-link-list'),
    path('share-links/<uuid:token>/', ShareLinkDetailView.as_view(), name='share-link-detail'),
    path('integrations/suno/callback/', SunoCallbackView.as_view(), name='suno-callback'),
]
