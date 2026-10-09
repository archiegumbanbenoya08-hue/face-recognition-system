import json
import os
from datetime import datetime

LOG_FILE = "event_log.jsonl"

def _ensure_log_dir():
    # Save log file at backend/ level
    pass


def log_event(event_type, student_id=None, location=None, status=None, details=None):
    """Append a recognition/event record to JSONL log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "student_id": student_id,
        "location": location,
        "status": status,
        "details": details,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_all_events():
    """Read all logged events."""
    if not os.path.exists(LOG_FILE):
        return []

    events = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    return events
