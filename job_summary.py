"""Render a Bandit JSON report as GitHub job summary Markdown.

Reads Bandit JSON on stdin, writes Markdown on stdout. Consumed by script.sh,
which appends the output to $GITHUB_STEP_SUMMARY.
"""

import json
import os
import sys
from collections import Counter
from typing import Any, Dict, List

# A job summary is capped at 1MiB per step; going over drops the whole summary
# and annotates the run with an error.
# https://docs.github.com/actions/reference/workflows-and-actions/workflow-commands
MAX_BYTES = 1024 * 1024 - 64 * 1024

MAX_LISTED = 50

SEVERITIES = ("HIGH", "MEDIUM", "LOW")

# Only the characters that let scanned content break out of a list item.
_MD_ESCAPE = str.maketrans({c: "\\" + c for c in "\\`*_[]<>|"})


def escape(text: Any) -> str:
    """Escape Markdown so scanned file names and messages cannot alter layout."""
    return " ".join(str(text).split()).translate(_MD_ESCAPE)


def rank(value: Any) -> int:
    """Order a severity or confidence label, sorting unrecognised ones last."""
    try:
        return SEVERITIES.index(str(value).upper())
    except ValueError:
        return len(SEVERITIES)


def render_counts(results: List[Dict[str, Any]]) -> List[str]:
    counts = Counter(str(r.get("issue_severity", "")).upper() for r in results)
    unknown = sum(n for sev, n in counts.items() if sev not in SEVERITIES)

    lines = [f"**Findings:** {len(results)}", "", "| Severity | Count |", "|---|---:|"]
    lines += [f"| {sev} | {counts[sev]} |" for sev in SEVERITIES]
    if unknown:
        lines.append(f"| UNKNOWN | {unknown} |")
    return lines


def render_findings(results: List[Dict[str, Any]]) -> List[str]:
    listed = sorted(results, key=lambda r: (
        rank(r.get("issue_severity")),
        rank(r.get("issue_confidence")),
        str(r.get("filename", "")).lower(),
        r.get("line_number") or 0,
    ))[:MAX_LISTED]

    heading = "### Top findings"
    if len(results) > len(listed):
        heading += f" (showing {len(listed)} of {len(results)})"

    lines = [heading, ""]
    for r in listed:
        lines.append(
            f"- **{escape(r.get('issue_severity', 'UNKNOWN'))}** "
            f"(confidence: {escape(r.get('issue_confidence', 'UNKNOWN'))}) "
            f"[{escape(r.get('test_id', '?'))}] "
            f"{escape(r.get('filename', '?'))}:{escape(r.get('line_number', '?'))}"
        )
        lines.append(f"  - {escape(r.get('issue_text', ''))}")
    return lines


def render_errors(errors: List[Dict[str, Any]]) -> List[str]:
    lines = [f"### Unscanned files ({len(errors)})", ""]
    lines += [
        "- {filename} — {reason}".format(
            filename=escape(err.get("filename", "?")),
            reason=escape(err.get("reason", "unknown error")),
        )
        for err in errors
    ]
    return lines


def render(report: Dict[str, Any]) -> List[str]:
    results = report.get("results") or []
    errors = report.get("errors") or []

    lines: List[str] = []
    if results:
        lines += render_counts(results) + [""] + render_findings(results)
    else:
        lines.append("No security issues found. ✅")
    if errors:
        lines += [""] + render_errors(errors)
    return lines


def truncate(body: str, max_bytes: int = MAX_BYTES) -> str:
    """Drop whole trailing lines until the body fits the job summary budget."""
    encoded = body.encode("utf-8")
    if len(encoded) <= max_bytes:
        return body

    notice = "\n\n_Summary truncated to fit the GitHub job summary size limit._"
    budget = max_bytes - len(notice.encode("utf-8"))
    clipped = encoded[:budget].decode("utf-8", "ignore")
    return clipped.rsplit("\n", 1)[0] + notice


def summarize(raw: str) -> str:
    title = f"## {os.getenv('INPUT_TOOL_NAME', 'bandit')} security report"
    try:
        report = json.loads(raw)
        if not isinstance(report, dict):
            raise ValueError("expected a JSON object")
    except ValueError as err:
        body = f"_Could not parse the Bandit report: {escape(err)}_"
    else:
        body = "\n".join(render(report))
    return truncate(f"{title}\n\n{body}\n")


if __name__ == "__main__":
    # Both Bandit's report and $GITHUB_STEP_SUMMARY are UTF-8 regardless of the
    # runner's locale, so neither stream may inherit its encoding from it.
    stdin = sys.stdin.buffer.read().decode("utf-8", "replace")
    sys.stdout.buffer.write(summarize(stdin).encode("utf-8"))
