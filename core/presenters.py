from .models import SongStatus
from .services.music_generation.strategies.mock_music_generation_strategy import MOCK_AUDIO_URL


def _present_audio_url(song):
    if song.audio_url:
        return song.audio_url
    if song.provider == 'mock' and song.status == SongStatus.READY:
        return MOCK_AUDIO_URL
    return ''


def present_song_summary(song):
    return {
        'id': song.id,
        'title': song.title,
        'provider': song.provider,
        'status': song.status,
        'duration': song.duration,
        'description': song.description,
        'audio_url': _present_audio_url(song),
        'occasion': song.occasion,
        'genre': song.genre,
        'voice_type': song.voice_type,
        'created_at': song.created_at.isoformat(),
    }


def present_song_detail(song):
    return {
        'id': song.id,
        'title': song.title,
        'provider': song.provider,
        'provider_generation_id': song.provider_generation_id,
        'status': song.status,
        'duration': song.duration,
        'description': song.description,
        'error_message': song.error_message,
        'audio_url': _present_audio_url(song),
        'occasion': song.occasion,
        'genre': song.genre,
        'voice_type': song.voice_type,
        'custom_text': song.custom_text,
        'created_at': song.created_at.isoformat(),
        'updated_at': song.updated_at.isoformat(),
    }


def present_song_generation(song):
    return {
        'id': song.id,
        'title': song.title,
        'provider': song.provider,
        'provider_generation_id': song.provider_generation_id,
        'status': song.status,
        'duration': song.duration,
        'description': song.description,
        'error_message': song.error_message,
        'audio_url': _present_audio_url(song),
    }


def present_user(user, include_created_at=True):
    payload = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }
    if include_created_at:
        payload['created_at'] = user.created_at.isoformat()
    return payload


def present_profile(profile):
    return {
        'id': profile.id,
        'user_id': profile.user_id,
        'gender': profile.gender,
        'birthday': profile.birthday.isoformat(),
    }


def present_share_link(link, include_validity=False):
    payload = {
        'id': link.id,
        'token': str(link.token),
        'expiration_date': link.expiration_date.isoformat(),
        'is_active': link.is_active,
    }
    if include_validity:
        payload['is_valid'] = link.is_valid
        payload['created_at'] = link.created_at.isoformat()
    return payload


def present_share_link_resolution(link):
    song = link.song
    return {
        'song_id': link.song_id,
        'token': str(link.token),
        'expiration_date': link.expiration_date.isoformat(),
        'title': song.title,
        'description': song.description,
        'audio_url': _present_audio_url(song),
        'duration': song.duration,
        'provider': song.provider,
    }
