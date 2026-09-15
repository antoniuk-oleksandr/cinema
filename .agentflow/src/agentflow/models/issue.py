from pydantic import BaseModel, ConfigDict, Field


class Issue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    severity: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    details: str | None = None
