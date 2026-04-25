from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderGenerationCommand:
    title: str
    prompt: str
    genre: str
