"""Ex Changed the Locks — one-liner entry for make.fun.

Bounty: u-xvader-tell-a-whole-story-in-32-characters-f86dd978
("Tell a whole story in 32 characters", $2, deadline 27 Nov 00:25 WIB).

The entry is a Wi-Fi network name (SSID) that tells a whole story in
24 characters: ``ExChangedLocksNotTheWiFi`` — an ex changed the locks,
but not the Wi-Fi (password). The joke only lands if the text is
exactly right, so this file treats the text as locked data and the
rest of the code as a small pipeline around it: validate, write,
verify. Nothing here is allowed to transform the text.

What this script does, in order:
  1. ``validate`` — rejects any text that would break the bounty rules
     (blank, whitespace-padded, multi-line, or over 32 characters).
  2. ``write_entry`` — writes the validated text to /output/entry.txt
     with no trailing newline, so the file is byte-identical to the
     text itself (24 bytes, not 25).
  3. ``verify_written`` — reads the file back and compares it byte
     for byte, so a truncated or mangled write fails loudly instead
     of shipping a malformed entry.
  4. ``main`` — wires the three steps together in that order.

Why split it this way: each step has one job and one failure mode,
so a future edit (or a reviewer) can see exactly which guarantee
broke, instead of debugging one big block that does everything.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Locked entry data — do not change a single character.
# ---------------------------------------------------------------------------
# The story, as a Wi-Fi name: "Ex changed locks, not the WiFi".
# 24 characters, no spaces, no punctuation — it must stay that way,
# because the bounty limit is 32 characters and the humour depends on
# the exact capitalisation (Ex / Changed / Locks / Not / The / WiFi).
TEXT = "ExChangedLocksNotTheWiFi"

# Where the make.fun harness expects the finished entry.
OUTPUT_PATH = Path("/output/entry.txt")

# Bounty limits: the story must fit in 32 characters, and an empty
# entry is not a story at all. Length is counted in characters here
# (the text is plain ASCII, so characters == UTF-8 bytes == file bytes).
MIN_LEN = 1
MAX_LEN = 32

# The exact bytes the file must contain. Built once, from the locked
# text, so the write step and the verify step compare against the same
# value and can never drift apart.
EXPECTED_BYTES = TEXT.encode("utf-8")


def validate(text: str) -> str:
    """Return ``text`` unchanged if it is a valid one-liner, else raise.

    Why this exists: the bounty rejects entries that are blank,
    padded with spaces, split over lines, or longer than 32
    characters. Catching that here — before anything is written —
    means a bad edit fails loudly in the terminal instead of
    silently producing a file the judges would reject.
    """
    if not text:
        raise ValueError("entry text must not be blank")
    if text != text.strip():
        raise ValueError("entry text must not have leading/trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry text must be a single line")
    size = len(text.encode("utf-8"))
    if not MIN_LEN <= size <= MAX_LEN:
        raise ValueError(
            f"entry text must be {MIN_LEN}-{MAX_LEN} UTF-8 characters, got {size}"
        )
    return text


def write_entry(text: str, path: Path = OUTPUT_PATH) -> int:
    """Write ``text`` to ``path`` with no trailing newline; return bytes.

    Why no newline: the harness reads the file as the entry itself.
    A trailing newline would make the file 25 bytes for a 24-character
    story and could count as an extra character. ``write_bytes`` (not
    ``write_text`` + a newline) makes the no-newline guarantee explicit.
    The parent directory is created first so the script also works on
    a fresh machine where /output does not exist yet.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    return path.write_bytes(data)


def verify_written(path: Path = OUTPUT_PATH, expected: bytes = EXPECTED_BYTES) -> None:
    """Read ``path`` back and require it to match ``expected`` byte for byte.

    Why this exists: a write can silently truncate (disk full, wrong
    path, a stray newline). Reading the file back and comparing bytes
    turns that silent corruption into a loud, immediate failure, so
    the entry that leaves this script is provably the entry that was
    intended. The comparison is on bytes, not on decoded text, so even
    an encoding slip would be caught.
    """
    actual = path.read_bytes()
    if actual != expected:
        raise AssertionError(
            f"round-trip mismatch: wrote {expected!r}, file contains {actual!r}"
        )


def main() -> None:
    """Validate the locked text, write it, then verify what was written."""
    text = validate(TEXT)
    written = write_entry(text)
    verify_written()
    print(f"Wrote {written} bytes ({len(text)} chars) to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
