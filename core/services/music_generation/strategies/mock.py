from .base import GenerationResult, MusicGenerationStrategy


class MockMusicGenerationStrategy(MusicGenerationStrategy):
    provider_name = 'mock'

    def generate(self, song):
        prompt = song.parameters
        description = (
            f"Mock song for {prompt.title} "
            f"({prompt.occasion}, {prompt.genre}, {prompt.voice_type})"
        )
        return GenerationResult(
            status='ready',
            duration=180,
            description=description,
            provider_generation_id=f'mock-song-{song.id}',
        )
