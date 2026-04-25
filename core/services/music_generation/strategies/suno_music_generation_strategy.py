from ..adapters import ProviderGenerationCommand, SunoApiAdapter
from .base import MusicGenerationStrategy


class SunoMusicGenerationStrategy(MusicGenerationStrategy):
    provider_name = 'suno'

    def __init__(self, client=None):
        self.client = client or SunoApiAdapter()

    def generate(self, song):
        command = ProviderGenerationCommand(
            title=song.title,
            prompt=song.custom_text.strip() or song.title,
            genre=song.genre,
        )
        return self.client.start_generation(command)
