import tomllib
from pathlib import Path

from pydantic import BaseModel, Field


class PipelineConfig(BaseModel):
    # A production/test/review cycle can consume three agent invocations.
    max_iterations: int = Field(12, ge=1)
    agent_timeout_seconds: float = Field(3600, gt=0)


class AgentConfig(BaseModel):
    developer: str = "developer"
    tester: str = "tester"
    reviewer: str = "reviewer"


class NotificationConfig(BaseModel):
    desktop: bool = True
    sound: bool = True


class Config(BaseModel):
    pipeline: PipelineConfig = PipelineConfig()
    agents: AgentConfig = AgentConfig()
    notifications: NotificationConfig = NotificationConfig()

    @classmethod
    def load(cls, path: Path):
        return cls.model_validate(tomllib.loads(path.read_text())) if path.exists() else cls()
