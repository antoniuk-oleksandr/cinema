import json
from datetime import UTC, datetime
from pathlib import Path


class SessionStore:
    ROLES = ("developer", "tester", "reviewer")

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self):
        if not self.path.exists():
            return {role: None for role in self.ROLES}
        data = json.loads(self.path.read_text())
        sessions = data.get("sessions", data)
        return {role: sessions.get(role) for role in self.ROLES}

    def save(self, sessions) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "updated_at": datetime.now(UTC).isoformat(),
            "sessions": {r: sessions.get(r) for r in self.ROLES},
        }
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(payload, indent=2) + "\n")
        temp.replace(self.path)
