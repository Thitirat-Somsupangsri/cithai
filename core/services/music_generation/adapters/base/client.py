from abc import ABC, abstractmethod


class MusicProviderClient(ABC):
    @abstractmethod
    def start_generation(self, command):
        raise NotImplementedError
