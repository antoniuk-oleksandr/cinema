from enum import StrEnum


class PipelineState(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    REVIEW = "review"
    DONE = "done"
    HUMAN_REQUIRED = "human_required"
