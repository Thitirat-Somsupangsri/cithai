from abc import ABC, abstractmethod
from dataclasses import dataclass


class SongGenerationError(Exception):
    pass


@dataclass
class GenerationResult:
    status: str
    duration: int = 0
    description: str = ''
    provider_generation_id: str = ''
    error_message: str = ''


class MusicGenerationStrategy(ABC):
    provider_name = ''

    @abstractmethod
    def generate(self, song):
        raise NotImplementedError
