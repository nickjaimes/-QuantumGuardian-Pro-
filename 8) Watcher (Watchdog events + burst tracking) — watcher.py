from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import threading, time, collections

from .risk import risk_for_event
from .quarantine import quarantine
from .utils import append_log, utcnow
from .settings import MONITORED_DIR, RISK_ALERT_THRESHOLD, RISK_QUARANTINE_THRESHOLD, LOG_FILE_NAME

class BurstCounter:
    def __init__(self, window=3.0):
        self.window = window
        self.events = collections.deque()  # (t, path)

    def add(self, path):
        now = time.time()
        self.events.append((now, path))
        while self.events and now - self.events[0][0] > self.window:
            self.events.popleft()
        return sum(1 for _, p in self.events if p == path)

class GuardianHandler(FileSystemEventHandler):
    def __init__(self, root: Path):
        self.root = root
        self.bursts = BurstCounter()

    def _handle(self, path: Path, kind: str):
        if not path or not path.is_file(): return
        burst = self.bursts.add(str(path))
        risk, details = risk_for_event(path, kind, burst)
        event = {
            "ts": utcnow(),
            "kind": kind,
            "path": str(path),
            "risk": risk,
            "details": details
        }
        append_log(self.root / LOG_FILE_NAME, event)

        # Console feedback
        if risk >= RISK_QUARANTINE_THRESHOLD:
            print(f"🔴 HIGH RISK {path.name} — {risk} → QUARANTINE")
            qinfo = quarantine(path, self.root)
            event["quarantine"] = qinfo
            append_log(self.root / LOG_FILE_NAME, event)
        elif risk >= RISK_ALERT_THRESHOLD:
            print(f"🟠 ALERT {path.name} — risk {risk}")
        else:
            print(f"🟢 OK {path.name} — risk {risk}")

    def on_created(self, e):  self._handle(Path(e.src_path), "created")
    def on_modified(self, e): self._handle(Path(e.src_path), "modified")
    def on_moved(self, e):    self._handle(Path(e.dest_path), "moved")
    def on_deleted(self, e):  self._handle(Path(e.src_path), "deleted")

def run_guardian():
    root = Path(MONITORED_DIR)
    root.mkdir(parents=True, exist_ok=True)
    handler = GuardianHandler(root)
    obs = Observer()
    obs.schedule(handler, str(root), recursive=True)
    obs.start()
    print(f"🛰  QuantumGuardian monitoring: {root}")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()
