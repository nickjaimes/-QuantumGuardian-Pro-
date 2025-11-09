from .features import extract_static_features, extract_behavioral_features
from .intel import intel_signals
from .fusion import trinity_fuse

def heuristic_score(static: dict) -> float:
    # Weighted rule-of-thumb
    score  = 0.35 * static["entropy_norm"]                # high entropy often packed/encrypted
    score += 0.25 * static["ext_susp"]                    # dangerous extensions
    score += 0.25 * min(static["size_mb"]/50.0, 1.0)      # very large or tiny can be odd; here: large
    score += 0.15 * static["name_hit"]                    # suspicious keyword in filename
    return max(0.0, min(score, 1.0))

def behavioral_score(behavior: dict) -> float:
    score  = 0.40 * behavior["event_modify"]
    score += 0.25 * behavior["event_create"]
    score += 0.15 * behavior["burst_norm"]
    score += 0.10 * behavior["cpu_norm"]
    score += 0.10 * behavior["event_move"]
    return max(0.0, min(score, 1.0))

def risk_for_event(path, event_kind, burst_count=1):
    static = extract_static_features(path)
    behavior = extract_behavioral_features(event_kind, burst_count)
    intel = intel_signals(path, static)

    # TRINITY-style fusion of partial beliefs
    risk = trinity_fuse(
        heuristic=heuristic_score(static),
        behavioral=behavioral_score(behavior),
        intel=intel["intel_score"]
    )

    return risk, {"static": static, "behavior": behavior, "intel": intel}
