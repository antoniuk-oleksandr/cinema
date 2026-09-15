from pydantic import BaseModel, ConfigDict, Field


class Task(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1)
    description: str = ""
    requirements: list[str] = []
    acceptance_criteria: list[str] = []
    constraints: list[str] = []
