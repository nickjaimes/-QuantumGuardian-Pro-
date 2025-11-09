from pathlib import Path
import math, re, psutil
from .utils import size_bytes

SUSPICIOUS_EXT = {".exe",".scr",".js",".vbs",".bat",".cmd",".dll",".jar",".lnk",".ps1",".apk",".pkg",".iso",".dmg",".rtf",".docm",".xlsm",".pptm"}
SUSPICIOUS_NAME_PAT = re.compile(r"(passwords?|secret|key|wallet|backup|invoice\d{3,}|urgent|report)", re.I)

def byte_entropy(path: Path, sample_bytes: int = 8192) -> float:
    try:
        with open(path, "rb") as f:
            data = f.read(sample_bytes)
        if not data: return 0.0
        freqs = [0]*256
        for b in data: freqs[b]+=1
        ent = 0.0
        for c in freqs:
            if c:
                p = c/len(data)
                ent -= p*math.log2(p)
        return ent/8.0  # normalize 0..1
    except Exception:
        return 0.0

def extract_static_features(path: Path) -> dict:
    ext = path.suffix.lower()
    sz = size_bytes(path)
    return {
        "ext": ext,
        "size_mb": sz/1_000_000,
        "entropy_norm": byte_entropy(path),
        "name_hit": 1.0 if SUSPICIOUS_NAME_PAT.search(path.name or "") else 0.0,
        "ext_susp": 1.0 if ext in SUSPICIOUS_EXT else 0.0,
    }

def extract_behavioral_features(event_kind: str, burst_count: int) -> dict:
    # Simple behavioral signals
    # burst_count = number of events for same path within short window
    cpu = psutil.cpu_percent(interval=None) / 100.0
    return {
        "event_create": 1.0 if event_kind=="created" else 0.0,
        "event_modify": 1.0 if event_kind=="modified" else 0.0,
        "event_move":   1.0 if event_kind=="moved" else 0.0,
        "event_delete": 1.0 if event_kind=="deleted" else 0.0,
        "burst_norm": min(burst_count/10.0, 1.0),
        "cpu_norm": min(cpu, 1.0),
    }
