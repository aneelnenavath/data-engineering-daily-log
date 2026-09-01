# Day 2 - Log File Parser

Stack: Python, regex (re module)

## Task

Parse a raw web server access log to extract the IP address, timestamp, and
HTTP status code from every line, then report the 5 most frequent status codes
and the 5 most frequent IP addresses.

## Files

- access.log - sample input: 30 lines, 6 distinct IPs, 6 distinct status codes
- log_parser.py - the parser script. Run with: python log_parser.py

## Key regex ideas used

- Digits are matched with \d, repeated with a quantifier like {1,3} or {3}
- A literal dot or bracket needs a backslash before it (\. or \[), because
  those characters mean something special in regex otherwise
- .* is a wildcard used to skip over parts of the line we do not care about
- Parentheses ( ) mark a capturing group - the exact piece of text we want
  pulled out, as opposed to text we are only using to anchor the pattern

## Why this design

- .* instead of spelling out every character: regex works best when you only
  describe precisely what you care about and let wildcards absorb the rest
- {3} for the status code but {1,3} for IP octets: status codes are always
  exactly 3 digits, IP octets can genuinely be 1, 2, or 3 digits
- re.findall on the whole file instead of a manual loop: since a dot does not
  match a newline by default, each match still stays confined to its own line

## How to run

python log_parser.py
