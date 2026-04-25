import json
import urllib.error
import urllib.request

from ..strategies.base import GenerationResult, SongGenerationError
from .base import MusicProviderClient
from .suno_config import SunoConfig


class SunoApiAdapter(MusicProviderClient):
    def start_generation(self, command):
        config = SunoConfig.from_settings()

        payload = {
            'customMode': config.custom_mode,
            'instrumental': config.instrumental,
            'callBackUrl': config.callback_url,
            'model': config.model,
            'prompt': command.prompt,
        }

        if config.custom_mode:
            payload['title'] = command.title
            payload['style'] = command.genre
            if config.instrumental:
                payload['prompt'] = ''

        request = urllib.request.Request(
            config.api_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {config.api_key}',
                'User-Agent': 'Mozilla/5.0 (compatible; Cithai/1.0)',
                'Accept': 'application/json',
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
            callback_url=config.callback_url,
        )
