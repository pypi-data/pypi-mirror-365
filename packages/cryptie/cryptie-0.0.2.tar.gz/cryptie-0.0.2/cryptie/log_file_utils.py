"""
Utilities for populating a log file showing CLI activity.
"""

import asyncio
from shlex import quote
from typing import Iterable, TextIO


def log_command(command: Iterable[str], file: TextIO | None) -> None:
    """
    Add a shell-style line to the log file for the provided command like::

        $ command arg1 arg2
    """
    if file is not None:
        file.write(f"$ {' '.join(map(quote, command))}\n")


async def record_stream(
    stream: asyncio.StreamReader, file: TextIO | None = None
) -> str:
    """
    A coroutine which will read from the provided stream (one line at a time),
    buffering the read data into a string. If a file is provided, also writes
    those lines to the file.
    """
    buffer = ""

    while line_bytes := await stream.readline():
        line = line_bytes.decode()
        buffer += line
        if file is not None:
            file.write(line)

    return buffer
