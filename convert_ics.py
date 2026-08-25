import re
import json
from datetime import datetime

with open("calendar.ics", "r", encoding="utf-8", errors="ignore") as f:
    raw = f.read()

# unfold lines per RFC 5545 (continuation lines start with space or tab)
raw = raw.replace("\r\n", "\n")
lines = []
for line in raw.split("\n"):
    if line.startswith(" ") or line.startswith("\t"):
        if lines:
            lines[-1] += line[1:]
    else:
        lines.append(line)

def ics_date_to_iso(value):
    digits = re.sub(r"[^0-9]", "", value)[:8]
    if len(digits) < 8:
        return None
    return f"{digits[0:4]}-{digits[4:6]}-{digits[6:8]}"

events = []
cur = None
for line in lines:
    if line.startswith("BEGIN:VEVENT"):
        cur = {}
    elif line.startswith("END:VEVENT"):
        if cur:
            events.append(cur)
        cur = None
    elif cur is not None:
        if line.startswith("DTSTART"):
            cur["start"] = ics_date_to_iso(line.split(":")[-1])
        elif line.startswith("DTEND"):
            cur["end"] = ics_date_to_iso(line.split(":")[-1])
        elif line.startswith("SUMMARY"):
            cur["summary"] = line.split(":", 1)[-1].strip()

events = [e for e in events if e.get("start") and e.get("end")]

output = {
    "updated": datetime.utcnow().isoformat() + "Z",
    "events": events
}

with open("calendar.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(events)} events")
