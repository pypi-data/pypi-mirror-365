import asyncio
from io import StringIO

import pytest

from cryptie.log_file_utils import log_command, record_stream


def test_log_command() -> None:
    file = StringIO()
    log_command(("foo", "bar", "baz qux"), file)

    assert file.getvalue() == "$ foo bar 'baz qux'\n"


@pytest.mark.parametrize("file", [None, StringIO()])
async def test_record_stream(file: StringIO | None) -> None:
    process = await asyncio.create_subprocess_exec(
        "echo",
        "Hello\nWorld",
        stdout=asyncio.subprocess.PIPE,
    )

    try:
        assert process.stdout is not None
        output = await record_stream(process.stdout, file)

        assert output == "Hello\nWorld\n"
        if file is not None:
            assert file.getvalue() == "Hello\nWorld\n"
    finally:
        await process.wait()
