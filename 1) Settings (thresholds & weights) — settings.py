# Risk thresholds
RISK_QUARANTINE_THRESHOLD = 0.80
RISK_ALERT_THRESHOLD = 0.60

# TRINITY fusion weights (sum ~= 1.0)
WEIGHT_HEURISTIC   = 0.45  # file-type rules, names, entropy
WEIGHT_BEHAVIORAL  = 0.30  # burst edits, process spikes
WEIGHT_INTEL       = 0.25  # local "intel" hits, extension mismatch

MONITORED_DIR = str(Path.home() / "Desktop")
QUARANTINE_DIR_NAME = ".guardian_quarantine"
LOG_FILE_NAME = "guardian.log"
