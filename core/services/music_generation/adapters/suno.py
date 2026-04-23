import json
import urllib.error
import urllib.request

from django.conf import settings

from ..strategies.base import GenerationResult, SongGenerationError
from .base import MusicProviderClient


class SunoApiAdapter(MusicProviderClient):
    def start_generation(self, command):
        api_key = getattr(settings, 'SUNO_API_KEY', '')
        api_url = getattr(settings, 'SUNO_API_URL', '').strip()
        callback_url = getattr(settings, 'SUNO_CALLBACK_URL', '').strip()
        model = getattr(settings, 'SUNO_MODEL', 'V4_5ALL')
        custom_mode = getattr(settings, 'SUNO_CUSTOM_MODE', False)
        instrumental = getattr(settings, 'SUNO_INSTRUMENTAL', False)

        if not api_key:
            raise SongGenerationError('Suno API key is not configured.')
        if not api_url:
            raise SongGenerationError('Suno API URL is not configured.')
        if not callback_url:
            raise SongGenerationError('Suno callback URL is not configured.')

        payload = {
            'customMode': custom_mode,
            'instrumental': instrumental,
            'callBackUrl': callback_url,
            'model': model,
            'prompt': command.prompt,
        }

        if custom_mode:
            payload['title'] = command.title
            payload['style'] = command.genre
            if instrumental:
                payload['prompt'] = ''

        request = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
            },
            method='POST',
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='ignore')
            raise SongGenerationError(f'Suno API request failed: {exc.code} {detail}') from exc
        except urllib.error.URLError as exc:
            raise SongGenerationError(f'Suno API is unreachable: {exc.reason}') from exc

        if body.get('code') != 200:
            raise SongGenerationError(body.get('msg', 'Suno generation failed.'))

        data = body.get('data') or {}
        task_id = str(data.get('taskId', ''))

        return GenerationResult(
            status='generating',
            duration=0,
            description=f'Suno generation started for "{command.title}"',
            provider_generation_id=task_id,
            error_message='',
        )
