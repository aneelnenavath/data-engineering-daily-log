# Day 2 Recap - Teaching a Computer to Read Server Logs

## The setup

Today's raw material was 30 lines of a fake web server access log, written in
the "Common Log Format" that real servers like Apache and Nginx produce
automatically for every single request. Unlike Day 1's CSV, this wasn't
neatly organized into columns - it was free-form text, and the task was to
pull three specific pieces of information (IP address, timestamp, status
code) out of that text using regex.

## Regex as a shape-description language

The core idea behind regex: instead of writing code that manually walks
through characters checking "is this a digit? is the next one a digit?",
you describe the shape of what you're looking for, and a specialized engine
finds it for you. Four pieces of vocabulary did almost all the work today:

- \d - a digit. \d{1,3} means "1 to 3 digits in a row" (an IP octet);
  \d{3} means "exactly 3 digits" (a status code, which is always exactly 3
  by spec - an important distinction between where you can be loose and
  where you should be precise).
- \w - a "word" character (letter, digit, or underscore). \w{3} matched
  the 3-letter month abbreviation in the timestamp.
- . and .* - a single dot alone means "any character at all"; .* means "any
  characters, any number of them, zero or more." This is regex's wildcard,
  and it's what let the pattern skip over the parts of each log line we
  didn't care about (the dash dash fields, the full HTTP request text) without
  having to describe them precisely.
- Escaping with backslash - characters like ., [, and ] mean something
  special in regex (any-character, start-of-character-class,
  end-of-character-class), so to match them literally - an actual period,
  an actual bracket - you prefix them with a backslash: \. \[ \]

## Capturing groups: the difference between matching and extracting

Parentheses ( ... ) around part of a pattern don't change what gets
matched - they change what you get to pull back out afterward. Without them,
match.group() gives you the entire matched text. With three sets of
parentheses around the IP, timestamp, and status code respectively,
match.groups() handed back exactly those three pieces as a tuple, ignoring
everything the wildcards skipped over. This is the mechanism that turns "find
this pattern somewhere in the text" into "extract these specific values."

## Two regex functions, two different jobs

re.search() finds the first match in a string and stops - useful while
building the pattern piece by piece against one line. re.findall() scans
the whole text and returns every match - what we switched to once the
pattern was working, applying it to all 30 lines glued together in one call
instead of looping manually. A detail worth remembering: a dot doesn't match a
newline character by default, so even glued into one big string, each match
stayed correctly confined to its own line.

## Counter, and the return of list comprehensions

from collections import Counter brought in a purpose-built tool for
"count how many times each thing appears" - exactly what "top 5" questions
need. Getting the data into the right shape for it used the same list
comprehension pattern from Day 1 ([r[0] for r in results]), just pulling a
different index out of each tuple - a reminder that a small number of core
patterns (boolean indexing, list comprehensions, capturing groups) get reused
constantly across very different problems.

## Real debugging, not scripted debugging

Today included three genuine hiccups, each one a legitimate lesson:

1. Pasting an indented block into the plain Python REPL broke. Multi-line
   with: blocks with indentation don't paste reliably into an interactive
   prompt - the terminal's paste and Python's own auto-indent interfere with
   each other. The fix was avoiding the indented block entirely
   (open(...).readlines() on one line) rather than fighting the paste
   behavior.
2. A nested code block in a README made copy-pasting confusing. Formatting
   inside formatting doesn't always render the way you'd expect - worth
   double-checking when something you're about to paste looks off, rather
   than pasting blindly.
3. git push failed with "Password authentication is not supported." GitHub
   retired plain password auth for git years ago; a stale cached credential
   on the machine was the culprit. The fix - git credential reject - to
   clear it, forcing a fresh browser-based sign-in - is worth remembering,
   since stale git credentials are a common real-world annoyance, not
   something unique to today.

## What to remember going into Day 3

Day 3 moves into SQL: window functions in SQLite (RANK, LAG/LEAD,
running totals). Different tool, but the habit stays the same - understand
each concept by running it and looking at the actual result, one deliberate
step at a time.
