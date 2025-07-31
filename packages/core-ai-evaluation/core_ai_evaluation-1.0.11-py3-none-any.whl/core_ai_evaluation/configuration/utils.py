import html
import re

_NEWLINES_PATTERN = re.compile(r"\n{3,}")
_SPACES_PATTERN = re.compile(r" {20,}")
_NON_PRINTABLE_PATTERN = re.compile(r"[\x00-\x09\x0B-\x1F\x7F]")


def adjust_indentation(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    if not lines:
        return ""
    non_empty = [line for line in lines if line.strip() != ""]
    if len(non_empty) <= 1:
        new_lines = [line.lstrip() for line in lines]
        return "\n".join(new_lines).strip()
    common_indent = None
    for line in non_empty:
        indent = re.match(r"^[ \t]*", line).group()
        if common_indent is None:
            common_indent = indent
        elif indent != common_indent:
            common_indent = ""
            break
    if common_indent:
        # Uniform indent found; preserve each line as is.
        return "\n".join(lines).strip()
    # Non-uniform indent: remove leading whitespace from all lines.
    new_lines = [line.lstrip() for line in lines]
    return "\n".join(new_lines).strip()


def clean_string(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    operations = [
        lambda s: s.replace("\xa0", " "),
        lambda s: _NEWLINES_PATTERN.sub("\n\n", s),
        lambda s: _SPACES_PATTERN.sub("  ", s),
        lambda s: s.replace("\u200b", ""),
        lambda s: _NON_PRINTABLE_PATTERN.sub("", s),
        lambda s: html.unescape(s),
    ]
    result = text
    for op in operations:
        result = op(result)
    return adjust_indentation(result)
