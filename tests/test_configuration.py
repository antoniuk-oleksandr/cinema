from pathlib import Path

from config.yaml_config import load_config


def test_yaml_profile_overrides_defaults(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "application.yaml").write_text("app:\n  environment: base\n  version: 1\n")
    (tmp_path / "application.test.yaml").write_text("app:\n  environment: test\n")
    monkeypatch.setenv("APP_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("APP_PROFILE", "test")
    config = load_config(tmp_path.parent)
    assert config["app"] == {"environment": "test", "version": 1}
