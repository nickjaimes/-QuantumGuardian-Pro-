from pathlib import Path
from .utils import sha256_of_file, safe_move, ensure_dir
from .settings import QUARANTINE_DIR_NAME

def quarantine(path: Path, base_dir: Path) -> dict:
    # Create hidden quarantine folder next to monitored dir
    qdir = ensure_dir(base_dir / QUARANTINE_DIR_NAME)
    info = {"original": str(path), "hash": None, "quarantined_to": None}

    try:
        if path.exists():
            info["hash"] = sha256_of_file(path)
            dst = safe_move(path, qdir)
            info["quarantined_to"] = str(dst)
    except Exception as e:
        info["error"] = str(e)
    return info
