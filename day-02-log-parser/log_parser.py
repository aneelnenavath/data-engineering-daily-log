"""
Day 2 - Log file parser.

Parses a web server access log (Common Log Format) to extract the IP address,
timestamp, and HTTP status code from every line using regex, then reports the
5 most frequent status codes and the 5 most frequent IP addresses.
"""

import re
from collections import Counter
from pathlib import Path

LOG_PATTERN = re.compile(
    r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'                  # IP address
    r'.*'
    r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})\]'   # timestamp
    r'.*'
    r'"\s(\d{3})\s\d+'                                        # status code
)


def parse_log(text: str) -> list[tuple[str, str, str]]:
    """Return a list of (ip, timestamp, status) tuples, one per matched line."""
    return LOG_PATTERN.findall(text)


def main() -> None:
    here = Path(__file__).parent
    log_path = here / "access.log"
    text = log_path.read_text()

    results = parse_log(text)
    print(f"Parsed {len(results)} log lines from {log_path.name}\n")

    ips = [r[0] for r in results]
    statuses = [r[2] for r in results]

    print("Top 5 status codes:")
    for status, count in Counter(statuses).most_common(5):
        print(f"  {status}: {count}")

    print("\nTop 5 IP addresses:")
    for ip, count in Counter(ips).most_common(5):
        print(f"  {ip}: {count}")


if __name__ == "__main__":
    main()
