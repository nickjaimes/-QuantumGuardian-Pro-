from pathlib import Path
import hashlib, json, time, os
from datetime import datetime

def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True); return p

def utcnow() -> str:
    return datetime.utcnow().isoformat() + "Z"

def append_log(logfile: Path, event: dict):
    ensure_dir(logfile.parent)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def size_bytes(path: Path) -> int:
    try: return path.stat().st_size
    except FileNotFoundError: return 0

def safe_move(src: Path, dst_dir: Path) -> Path:
    ensure_dir(dst_dir)
    dst = dst_dir / (src.name + f".{int(time.time())}")
    try:
        src.rename(dst)
        return dst
    except Exception:
        # Cross-device move fallback
        import shutil; shutil.move(str(src), str(dst))
        return dst
