from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .issue import Issue

type JsonValue = str | int | float | bool | list["JsonValue"] | dict[str, "JsonValue"] | None


class Route(StrEnum):
    DEVELOPER = "developer"
    TESTER = "tester"
    REVIEWER = "reviewer"
    BOTH = "both"
    DONE = "done"
    HUMAN_REQUIRED = "human_required"


class AgentStatus(StrEnum):
    COMPLETED = "completed"
    CHANGES_REQUIRED = "changes_required"
    APPROVED = "approved"
    BLOCKED = "blocked"
    ERROR = "error"


class AgentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: AgentStatus
    route: Route
    summary: str | None = None
    issues: list[Issue] = Field(default_factory=list)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def coherent(self):
        if self.status == AgentStatus.APPROVED and self.route != Route.DONE:
            raise ValueError("approved must route done")
        if self.route == Route.DONE and self.status != AgentStatus.APPROVED:
            raise ValueError("done must be approved")
        if (
            self.route in (Route.DEVELOPER, Route.TESTER, Route.BOTH)
            and self.status != AgentStatus.CHANGES_REQUIRED
        ):
            raise ValueError("change routes require changes_required")
        if self.status == AgentStatus.COMPLETED and self.route not in (
            Route.TESTER,
            Route.REVIEWER,
        ):
            raise ValueError("completed must hand off")
        return self
