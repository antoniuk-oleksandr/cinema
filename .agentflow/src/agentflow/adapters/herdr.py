from .codex import CodexAdapter


class HerdrAdapter(CodexAdapter):
    """Herdr 0.9.0 exposes agent prompt/wait APIs; this conservative adapter delegates
    execution to Codex exec until named persistent agent provisioning is configured."""

