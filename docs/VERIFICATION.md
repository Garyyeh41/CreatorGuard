# Verification

Verified locally on 2026-10-12 (Asia/Taipei).

## Unit tests

```bash
python -m unittest discover -s tests -v
```

Result: **7 tests passed**. The tests cover timestamp conversion, a valid cue, overlap, reversed duration, line length, preservation of source cue numbers in findings, and the specific missing-text warning. The recorded run is in [TEST_RESULTS.txt](TEST_RESULTS.txt).

## CLI examples

| Input | Findings | Exit code |
| --- | --- | --- |
| `examples/valid.srt` | 0 | 0 |
| `examples/review_needed.srt` | 3 warnings: line length, overlap, line count | 0 |

The JSON reports in `examples/reports/` were produced by running the checked-in program on these synthetic files. Warning-only reports intentionally return exit code 0; reviewers must read the findings.

## Preparation changes

The recovered prototype was retained as the starting point. Two narrow diagnostic corrections were made for this repository:

1. Findings now identify the source SRT cue number when it is valid, including nonsequential numbering. Previously they used the block position.
2. A cue with a valid time range and no subtitle text now receives `No subtitle text`. Previously it incorrectly received a malformed-time-range error.

Both changes have regression tests. The archived historical program and production evidence were not modified.

## Limits of verification

These checks establish only the tested rule-based behavior. They do not validate vocal synchronization, translation, visual detection, AI accuracy, or ASUS UGen300 execution. There has been no hardware benchmark or accelerator validation in this repository.
