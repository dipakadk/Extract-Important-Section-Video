import re


_TIMESTAMP_PATTERN = re.compile(r"^(\d+):([0-5]\d):([0-5]\d)(?:\.(\d{1,3}))?$")
_BOUNDARY_TOLERANCE_MS = 1000


def timestamp_to_milliseconds(timestamp: str) -> int:
    match = _TIMESTAMP_PATTERN.fullmatch(timestamp)
    if match is None:
        raise ValueError(f"Invalid timestamp: {timestamp!r}")

    hours, minutes, seconds, fraction = match.groups()
    milliseconds = int((fraction or "0").ljust(3, "0"))
    return (
        int(hours) * 3_600_000
        + int(minutes) * 60_000
        + int(seconds) * 1000
        + milliseconds
    )


def _format_timestamp(milliseconds: int) -> str:
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


def _nearest_cue_boundary(timestamp_ms: int, cues, boundary_index: int):
    nearby_cues = [
        cue
        for cue in cues
        if max(cue[0] - timestamp_ms, 0, timestamp_ms - cue[1]) <= _BOUNDARY_TOLERANCE_MS
    ]
    if not nearby_cues:
        return None

    cue = min(nearby_cues, key=lambda item: abs(timestamp_ms - item[boundary_index]))
    return cue[boundary_index]


def validate_section_timestamps(sections, srt_file_path):
    """Snap supported section boundaries to SRT cues and reject invalid ranges."""
    import pysrt

    cues = [
        (subtitle.start.ordinal, subtitle.end.ordinal)
        for subtitle in pysrt.open(srt_file_path)
    ]
    if not cues:
        return []

    validated_sections = []
    for section in sections:
        try:
            start_ms = timestamp_to_milliseconds(section.start_timestamp)
            end_ms = timestamp_to_milliseconds(section.end_timestamp)
        except (AttributeError, TypeError, ValueError):
            continue

        if start_ms >= end_ms:
            continue

        aligned_start = _nearest_cue_boundary(start_ms, cues, 0)
        aligned_end = _nearest_cue_boundary(end_ms, cues, 1)
        if aligned_start is None or aligned_end is None or aligned_start >= aligned_end:
            continue

        validated_sections.append(
            section.model_copy(
                update={
                    "start_timestamp": _format_timestamp(aligned_start),
                    "end_timestamp": _format_timestamp(aligned_end),
                }
            )
        )

    return validated_sections