from abc import ABC, abstractmethod


class MusicGenerationStrategy(ABC):
    provider_name = ''

    @abstractmethod
    def generate(self, song):
        raise NotImplementedError
