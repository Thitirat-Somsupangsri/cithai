from .user_views import UserListView, UserDetailView
from .profile_views import ProfileView
from .song_views import SongListView, SongDetailView
from .share_link_views import ShareLinkListView, ShareLinkDetailView
from .music_generation_callback_views import SunoCallbackView
from .google_login_view import GoogleLoginView
from .google_callback_view import GoogleCallbackView

__all__ = [
    'UserListView', 'UserDetailView',
    'ProfileView',
    'SongListView', 'SongDetailView',
    'ShareLinkListView', 'ShareLinkDetailView',
    'GoogleLoginView', 'GoogleCallbackView',
    'SunoCallbackView',
]

