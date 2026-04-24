import json
from unittest.mock import patch

from django.test import TestCase, override_settings

from core.services.music_generation.adapters import ProviderGenerationCommand, SunoApiAdapter


class SunoApiAdapterTests(TestCase):
    @override_settings(
        SUNO_API_KEY='secret',
        SUNO_API_URL='https://api.sunoapi.org/api/v1/generate',
        SUNO_CALLBACK_URL='https://my-app.trycloudflare.com/integrations/suno/callback/',
        SUNO_MODEL='V4_5ALL',
        SUNO_CUSTOM_MODE=True,
        SUNO_INSTRUMENTAL=False,
    )
    @patch('core.services.music_generation.adapters.suno.urllib.request.urlopen')
    def test_adapter_maps_successful_response(self, mock_urlopen):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps({'code': 200, 'data': {'taskId': 'abc-123'}}).encode('utf-8')

        mock_urlopen.return_value = FakeResponse()
        adapter = SunoApiAdapter()

        result = adapter.start_generation(
            ProviderGenerationCommand(
                title='Test Song',
                prompt='test prompt',
                genre='rock',
            )
        )

        self.assertEqual(result.status, 'generating')
        self.assertEqual(result.provider_generation_id, 'abc-123')

        request = mock_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode('utf-8'))
        self.assertEqual(payload['title'], 'Test Song')
        self.assertEqual(payload['style'], 'rock')
        self.assertEqual(payload['prompt'], 'test prompt')

    @override_settings(
        SUNO_API_KEY='',
        SUNO_API_URL='https://api.sunoapi.org/api/v1/generate',
        SUNO_CALLBACK_URL='https://my-app.trycloudflare.com/integrations/suno/callback/',
    )
    def test_adapter_rejects_missing_config(self):
        adapter = SunoApiAdapter()

        with self.assertRaisesMessage(Exception, 'Suno API key is not configured.'):
            adapter.start_generation(
                ProviderGenerationCommand(
                    title='Test Song',
                    prompt='prompt',
                    genre='pop',
                )
            )
