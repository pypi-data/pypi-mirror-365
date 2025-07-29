import asyncio
from io import StringIO
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from cryptie.gpg.shell import (
    GPGShell,
    StatusLine,
    UnexpectedEOFError,
    UnexpectedStatusError,
)


class TestGPGShell:
    async def test_readline_and_unreadline(self) -> None:
        mock_reader = AsyncMock()
        shell = GPGShell(cast(asyncio.StreamReader, mock_reader))

        mock_reader.readline.side_effect = [b"foo\n", b"bar\n", b"baz\n", b""]

        # Readline
        assert await shell._readline() == "foo\n"
        assert await shell._readline() == "bar\n"

        # Unread
        shell._unreadline("bar\n")
        assert await shell._readline() == "bar\n"
        assert await shell._readline() == "baz\n"
        assert await shell._readline() == ""

    async def test_read_status_line(self) -> None:
        mock_reader = AsyncMock()
        shell = GPGShell(cast(asyncio.StreamReader, mock_reader))

        mock_reader.readline.side_effect = [
            b"[GNUPG:] HELLO",
            b"[GNUPG:] HELLO 1 2 3\n",
        ]

        assert await shell.read_status_line() == StatusLine("HELLO")
        assert await shell.read_status_line() == StatusLine("HELLO", ("1", "2", "3"))

    async def test_read_status_line_eof(self) -> None:
        mock_reader = AsyncMock()
        shell = GPGShell(cast(asyncio.StreamReader, mock_reader))

        mock_reader.readline.side_effect = [b""]
        assert await shell.read_status_line() is None

    async def test_read_status_line_non_status(self) -> None:
        mock_reader = AsyncMock()
        shell = GPGShell(cast(asyncio.StreamReader, mock_reader))

        mock_reader.readline.side_effect = [b"nope", b""]
        assert await shell.read_status_line() is None

        mock_reader.readline.side_effect = [b"nope", b"[GNUPG:] FOO"]
        assert await shell.read_status_line() == StatusLine("FOO")

    async def test_read_non_status_line_to_eof(self) -> None:
        mock_reader = AsyncMock()
        shell = GPGShell(cast(asyncio.StreamReader, mock_reader))

        mock_reader.readline.side_effect = [b"non-status\n", b""]
        assert await shell.read_non_status_line() == "non-status\n"
        assert await shell.read_non_status_line() is None

    async def test_read_non_status_line_to_status_line(self) -> None:
        mock_reader = AsyncMock()
        shell = GPGShell(cast(asyncio.StreamReader, mock_reader))

        mock_reader.readline.side_effect = [b"non-status\n", b"[GNUPG:] FOO"]
        assert await shell.read_non_status_line() == "non-status\n"
        assert await shell.read_non_status_line() is None

        assert await shell.read_status_line() == StatusLine("FOO")

    async def test_read_non_status_lines(self) -> None:
        mock_reader = AsyncMock()
        shell = GPGShell(cast(asyncio.StreamReader, mock_reader))

        mock_reader.readline.side_effect = [
            b"non-status\n",
            b"also-non-status\n",
            b"[GNUPG:] FOO",
        ]
        assert await shell.read_non_status_lines() == "non-status\nalso-non-status\n"
        assert await shell.read_non_status_lines() is None

        assert await shell.read_status_line() == StatusLine("FOO")

    async def test_write_line(self) -> None:
        mock_reader = AsyncMock()
        mock_writer = AsyncMock(write=Mock())
        shell = GPGShell(
            cast(asyncio.StreamReader, mock_reader),
            cast(asyncio.StreamWriter, mock_writer),
        )

        await shell.write_line("foobar")
        mock_writer.write.assert_called_once_with(b"foobar\n")
        mock_writer.drain.assert_called_once()

    async def test_assemble_argument_constraints(self) -> None:
        shell = GPGShell(cast(asyncio.StreamReader, AsyncMock()))

        out = shell._normalise_argument_constraints("foo", "bar", arg_10="baz")
        assert out == {
            0: "foo",
            1: "bar",
            10: "baz",
        }

    async def test_assemble_argument_constraints_invalid(self) -> None:
        shell = GPGShell(cast(asyncio.StreamReader, AsyncMock()))

        with pytest.raises(TypeError):
            shell._normalise_argument_constraints(arg_foo="bar")

    async def test_match_argument_constraints_type_only(self) -> None:
        shell = GPGShell(cast(asyncio.StreamReader, AsyncMock()))

        status = StatusLine("FOO", ("bar", "baz"))

        assert shell._match_argument_constraints(status, "FOO", {}) is True
        assert shell._match_argument_constraints(status, "BAR", {}) is False

    async def test_match_argument_constraints_args(self) -> None:
        shell = GPGShell(cast(asyncio.StreamReader, AsyncMock()))

        status = StatusLine("FOO", ("bar", "baz"))

        assert shell._match_argument_constraints(status, "FOO", {0: "bar"}) is True
        assert (
            shell._match_argument_constraints(status, "FOO", {0: "bar", 1: "baz"})
            is True
        )
        assert shell._match_argument_constraints(status, "FOO", {0: "qux"}) is False
        assert shell._match_argument_constraints(status, "FOO", {3: "qux"}) is False

    async def test_expect_status_eof(self) -> None:
        mock_reader = AsyncMock()
        shell = GPGShell(cast(asyncio.StreamReader, mock_reader))

        mock_reader.readline.side_effect = [b""]

        with pytest.raises(UnexpectedEOFError) as exc_info:
            assert await shell.expect_status("FOO")
        assert str(exc_info.value) == "Unexpected end of stream. Expected FOO ..."

    async def test_expect_status(self) -> None:
        mock_reader = AsyncMock()
        shell = GPGShell(cast(asyncio.StreamReader, mock_reader))

        mock_reader.readline.side_effect = [b"[GNUPG:] FOO 1 2 3\n", b"[GNUPG:] BAR\n"]

        assert await shell.expect_status("FOO", "1", "2") == StatusLine(
            "FOO", ("1", "2", "3")
        )

        with pytest.raises(UnexpectedStatusError) as exc_info:
            assert await shell.expect_status("FOO", "1", arg_2="3")
        assert (
            str(exc_info.value)
            == "Unexpected status BAR. Expected FOO 1 <anything> 3 ..."
        )

    async def test_skip_while_status(self) -> None:
        mock_reader = AsyncMock()
        shell = GPGShell(cast(asyncio.StreamReader, mock_reader))

        mock_reader.readline.side_effect = [
            b"[GNUPG:] FOO\n",
            b"[GNUPG:] FOO 1 2 3\n",
            b"[GNUPG:] BAR\n",
            b"[GNUPG:] FOO\n",
            b"[GNUPG:] BAR 1 2 3\n",
            b"",
            b"",
        ]

        await shell.skip_while_status("FOO")
        assert await shell.expect_status("BAR") == StatusLine("BAR")

        await shell.skip_while_status("FOO")
        assert await shell.expect_status("BAR") == StatusLine("BAR", ("1", "2", "3"))

        await shell.skip_while_status("FOO")
        assert await shell.read_status_line() is None

    async def test_send_command(self) -> None:
        mock_reader = AsyncMock()
        mock_writer = AsyncMock(write=Mock())
        shell = GPGShell(
            cast(asyncio.StreamReader, mock_reader),
            cast(asyncio.StreamWriter, mock_writer),
        )

        mock_reader.readline.side_effect = [b"[GNUPG:] GOT_IT", b""]

        await shell.send_command("foobar")
        mock_writer.write.assert_called_once_with(b"foobar\n")
        mock_writer.drain.assert_called_once()

        assert await shell.read_status_line() is None

    async def test_logging(self) -> None:
        mock_reader = AsyncMock()
        mock_writer = AsyncMock(write=Mock())
        log_file = StringIO()
        shell = GPGShell(
            cast(asyncio.StreamReader, mock_reader),
            cast(asyncio.StreamWriter, mock_writer),
            log_file=log_file,
        )

        mock_reader.readline.side_effect = [b"[GNUPG:] GOT_IT\n", b""]
        await shell.send_command("foobar")

        assert log_file.getvalue() == "foobar\n[GNUPG:] GOT_IT\n"
