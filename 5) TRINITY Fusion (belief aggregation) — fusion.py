from .settings import WEIGHT_HEURISTIC, WEIGHT_BEHAVIORAL, WEIGHT_INTEL

def trinity_fuse(*, heuristic: float, behavioral: float, intel: float) -> float:
    # Weighted sum + soft-boost when two or more agree
    base = (WEIGHT_HEURISTIC*heuristic +
            WEIGHT_BEHAVIORAL*behavioral +
            WEIGHT_INTEL*intel)
    agrees = sum(x>0.6 for x in (heuristic, behavioral, intel))
    if agrees >= 2:
        base = min(base + 0.10, 1.0)
    return round(base, 3)
