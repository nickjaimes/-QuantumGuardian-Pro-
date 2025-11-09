from pathlib import Path
import re

MISMATCH = {
    ".pdf":  b"%PDF",
    ".png":  b"\x89PNG",
    ".jpg":  b"\xff\xd8",
    ".zip":  b"PK\x03\x04",
    ".exe":  b"MZ",
    ".docx": b"PK\x03\x04",
}

BLOCKLIST_PAT = re.compile(r"(stealer|ransom|crypto|inject|keylogger|trojan)", re.I)

def extension_header_mismatch(path: Path, ext: str) -> float:
    magic = MISMATCH.get(ext)
    if not magic: return 0.0
    try:
        with open(path, "rb") as f:
            head = f.read(len(magic))
        return 1.0 if head and not head.startswith(magic) else 0.0
    except Exception:
        return 0.0

def intel_signals(path: Path, static: dict) -> dict:
    ext = static["ext"]
    header_mismatch = extension_header_mismatch(path, ext)
    block_hit = 1.0 if BLOCKLIST_PAT.search(path.name) else 0.0
    intel_score = min(0.6*header_mismatch + 0.4*block_hit, 1.0)
    return {"header_mismatch": header_mismatch, "block_hit": block_hit, "intel_score": intel_score}
