from .base import GenerationResult, MusicGenerationStrategy

MOCK_AUDIO_URL = '/mock-song.mp3'
MOCK_AUDIO_DURATION_SECONDS = 9


class MockMusicGenerationStrategy(MusicGenerationStrategy):
    provider_name = 'mock'

    def generate(self, song):
        return GenerationResult(
            status='ready',
            duration=MOCK_AUDIO_DURATION_SECONDS,
            description=f'Mock generation complete for "{song.title}"',
            audio_url=MOCK_AUDIO_URL,
            provider_generation_id=f'mock-{song.id}',
        )
