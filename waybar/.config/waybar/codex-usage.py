#!/usr/bin/env python3
"""Waybar Codex limits from local session snapshots; never reads credentials."""
import datetime as dt
import html
import json
import os
from pathlib import Path
import time


def latest_snapshot(root):
    latest = None
    # Read backwards so large conversations do not need to be loaded into memory.
    for path in root.rglob('*.jsonl'):
        try:
            with path.open('rb') as stream:
                stream.seek(0, 2)
                position = stream.tell()
                pending = b''
                found = False
                while position and not found:
                    size = min(position, 65536)
                    position -= size
                    stream.seek(position)
                    parts = (stream.read(size) + pending).split(b'\n')
                    pending = parts.pop(0)
                    if position == 0:
                        parts.insert(0, pending)
                    for line in reversed(parts):
                        if b'"rate_limits"' not in line:
                            continue
                        try:
                            event = json.loads(line)
                            limits = event.get('payload', {}).get('rate_limits')
                            if not limits or limits.get('limit_id') not in (None, 'codex'):
                                continue
                            if not limits.get('primary') and not limits.get('secondary'):
                                continue
                            timestamp = dt.datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')).timestamp()
                        except (ValueError, KeyError, TypeError):
                            continue
                        if latest is None or timestamp > latest[0]:
                            latest = (timestamp, limits)
                        found = True
                        break
        except OSError:
            continue
    return latest


def render(snapshot, now):
    if snapshot is None:
        return {'text': '󰚩 —', 'class': 'unknown', 'tooltip': 'No Codex usage snapshot yet. Use Codex to populate local session logs.'}
    timestamp, limits = snapshot
    age = max(0, now - timestamp)
    stale = age > 900
    pieces, details, percentages = [], ['Codex usage · percentage remaining'] , []
    for key, label in [('primary', '5h'), ('secondary', 'week')]:
        window = limits.get(key)
        if not window:
            pieces.append(f'{label} —')
            continue
        used = float(window['used_percent'])
        reset = window.get('resets_at')
        expired = reset is not None and reset <= now
        pieces.append(f'{label} {"?" if expired else f"{max(0, 100 - used):g}%"}')
        if not expired:
            percentages.append(used)
        details.append(f'{label}: {max(0, 100 - used):g}% remaining (last reported)')
        if reset:
            date = dt.datetime.fromtimestamp(reset).astimezone().strftime('%a %b %d, %H:%M %Z')
            details.append(f'  Reset: {date}' + (' · awaiting fresh snapshot' if expired else ''))
    updated = dt.datetime.fromtimestamp(timestamp).astimezone().strftime('%b %d, %H:%M:%S %Z')
    details.extend(['', f'Last snapshot: {updated}', 'Reads local Codex logs every 30 seconds.', 'New readings arrive when Codex reports usage.'])
    if stale:
        details.append('Snapshot is older than 15 minutes.')
    level = max(percentages, default=0)
    state = 'critical' if level >= 95 else 'warning' if level >= 80 else 'normal'
    return {'text': '󰚩 ' + pieces[0].removeprefix('5h ') + (' ~' if stale else ''), 'class': [state] + (['stale'] if stale else []), 'tooltip': html.escape('\n'.join(details))}


if __name__ == '__main__':
    root = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'sessions'
    try:
        output = render(latest_snapshot(root), time.time())
    except (ValueError, TypeError, OverflowError):
        output = {'text': '󰚩 —', 'class': 'unknown', 'tooltip': 'Could not parse the local Codex usage snapshot.'}
    print(json.dumps(output))
