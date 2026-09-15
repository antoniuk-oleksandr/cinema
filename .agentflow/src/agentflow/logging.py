import logging
from pathlib import Path


def configure(root: Path) -> None:
    log = root / "runtime"
    log.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log / "agentflow.log")],
    )
