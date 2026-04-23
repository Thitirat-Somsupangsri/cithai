from dataclasses import dataclass


@dataclass
class GenerationResult:
    status: str
    duration: int = 0
    description: str = ''
    provider_generation_id: str = ''
    error_message: str = ''
