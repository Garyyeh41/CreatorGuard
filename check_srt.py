"""Small, honest SRT quality-checking prototype; not a visual AI checker."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

STAMP = re.compile(r"^(\d{2}):(\d{2}):(\d{2})[,.](\d{3})$")

def ms(s: str) -> int:
    m = STAMP.fullmatch(s.strip())
    if not m:
        raise ValueError(f"Invalid SRT time stamp: {s!r}")
    h, minute, sec, milli = (int(x) for x in m.groups())
    if minute > 59 or sec > 59:
        raise ValueError(f"Invalid minute/second: {s!r}")
    return ((h * 60 + minute) * 60 + sec) * 1000 + milli

def inspect(text: str, max_chars: int = 42, max_lines: int = 2) -> list[dict]:
    messages: list[dict] = []
    blocks = re.split(r"\n\s*\n", text.replace('\ufeff', '').replace('\r\n', '\n').strip())
    prev_end = -1
    for n, block in enumerate(blocks, 1):
        lines = block.strip().splitlines()
        if not lines or not lines[0].strip().isdigit():
            messages.append({'cue': n, 'level': 'ERROR', 'issue': 'Invalid cue index'}); continue
        n = int(lines[0].strip())
        if len(lines) < 2 or ' --> ' not in lines[1]:
            messages.append({'cue': n, 'level': 'ERROR', 'issue': 'Missing or malformed time range'}); continue
        try:
            start, end = (ms(x) for x in lines[1].split(' --> ', 1))
        except ValueError as exc:
            messages.append({'cue': n, 'level': 'ERROR', 'issue': str(exc)}); continue
        if end <= start:
            messages.append({'cue': n, 'level': 'ERROR', 'issue': 'Non-positive cue duration'})
        if start < prev_end:
            messages.append({'cue': n, 'level': 'WARNING', 'issue': 'Overlapping cues'})
        prev_end = max(prev_end, end)
        subtitle_lines = [l.strip() for l in lines[2:] if l.strip()]
        if len(subtitle_lines) > max_lines:
            messages.append({'cue': n, 'level': 'WARNING', 'issue': f'Too many lines: {len(subtitle_lines)}'})
        for j, line in enumerate(subtitle_lines, 1):
            if len(line) > max_chars:
                messages.append({'cue': n, 'level': 'WARNING', 'issue': f'Line {j}: {len(line)} > {max_chars} characters'})
        if not subtitle_lines:
            messages.append({'cue': n, 'level': 'WARNING', 'issue': 'No subtitle text'})
    return messages

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=Path)
    parser.add_argument('--max-chars', type=int, default=42)
    args = parser.parse_args()
    errors = inspect(args.path.read_text(encoding='utf-8-sig'), args.max_chars)
    print(json.dumps({'file': args.path.name, 'findings': errors, 'finding_count': len(errors)}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if any(x['level'] == 'ERROR' for x in errors) else 0)
if __name__ == '__main__':
    main()
