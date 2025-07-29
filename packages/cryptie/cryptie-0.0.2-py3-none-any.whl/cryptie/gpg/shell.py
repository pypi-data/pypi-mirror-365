r"""
Utilities for interacting with GnuPG interactive shells.
========================================================

GnuPG provides various options enable a machine-friendly, stable interface to
GnuPG's interactive shell-style UIs. The specification for this can be found in
the `DETAILS`_ document in the GnuPG documentation. An overview of the salient
points is given below.

.. DETAILS: https://github.com/gpg/gnupg/blob/master/doc/DETAILS

Usage example::

    >>> # Start a GPG shell command in machine-readable mode
    >>> proc = await asyncio.create_subprocess_exec(
    ...     "gpg",
    ...     "--with-colons",  # Enable machine-parsable interface
    ...     "--command-fd=0",  # Input on stdin
    ...     "--status-fd=1",  # Output on stdout
    ...     "--card-edit",
    ...     stdin=asyncio.subprocess.PIPE,
    ...     stdout=asyncio.subprocess.PIPE,
    ... )
    >>> shell = GPGShell(proc.stdout, proc.stdin)

    >>> # This command initially outputs a "CARDCTRL 3" status if a Yubikey is
    >>> # found, then outputs colon-delimited details of that card.
    >>> await shell.expect_status("CARDCTRL", "3")
    >>> details = await shell.read_non_status_lines()

    >>> # Typical interactions with the shell involve a back-and-forth of
    >>> # "GET_LINE" requests to respond to.
    >>> await shell.expect_status("GET_LINE", "cardedit.prompt")
    >>> await shell.send_command("admin")
    
    >>> # Sometimes you may wish to ignore status lines, for example
    >>> # PINENTRY_LAUNCHED, especially as these may or may not occur depending
    >>> # on the state of the card.
    >>> await shell.skip_while_status("PINENTRY_LAUNCHED")


Enabling machine readable mode
------------------------------

GnuPG's interactive commands can be placed into machine-readable mode by
passing the following arguments:

* ``--no-tty`` Ensure all other messages go to stderr, not the TTY
* ``--status-fd <NUM>`` Output command status in machine-readable mode on
  the given file descriptor. 1 (stdout) is usually used.
* ``--command-fd <NUM>`` Read command in machine-readable mode on
  the given file descriptor. 0 (stdin) is usually used.
* ``--with-colons`` Format all output data as colon-separated values with a
  stable output ordering.


Output format primer
--------------------

GnuPG's output lines can be divided into two categories: "status" lines (e.g.
prompts) and non-status lines (for other information).

Status lines always have the format::

    [GNUPG:] type arg0 arg1 ...

Where 'type' is the type of the status line (e.g. ``GET_LINE`` which indicates
that some form of input is required) followed by a series of space-delimited
type-specific arguments. This interface is intended to be stable with new
versions of GnuPG only adding new arguments.

Non-status lines do not begin with the ``[GNUPG:] `` marker and are often
colon-separated values (due to ``--with-colons``). These lines tend to contain
secondary, or more detailed information with all control-flow being via status
lines.


Typical interaction pattern
---------------------------

A typical interactive session involves reading ``GET_LINE`` status lines and
responding accordingly with a newline-terminated response.

Each ``GET_LINE`` status' zeroth argument is a string identifying what is being
requested from the user. These look like ``cardedit.prompt`` and correspond to
GnuPG's translation strings -- looking these up in the GnuPG source will reveal
the equivalent user-facing message. For example ``cardedit.prompt`` is the
ordinary prompt for the ``--card-edit`` shell and means GnuPG wants us to enter
a shell command.

To respond, a newline-terminated value should be sent to to the command file
descriptor. For example we might respond to ``cardedit.prompt`` with
``generate\n`` to run the 'generate' command. GnuPG will respond to this
immediately with a ``GOT_IT`` status line.

Other status lines may be used at various times. For example the
``--card-edit`` shell starts by sending a ``CARDCTRL`` line indicating whether
it has successfully connected to a card. As another example, whenever a PIN is
requested from the user the ``PINENTRY_LAUNCHED`` status line is sent.
"""

import asyncio
from dataclasses import dataclass
from typing import NamedTuple, TextIO


class StatusLine(NamedTuple):
    """A status line read from GnuPG."""

    type: str
    args: tuple[str, ...] = ()

    def __str__(self) -> str:
        out = self.type
        for arg in self.args:
            out += f" {arg}"
        return out


@dataclass
class GPGShellError(Exception):
    """Base for GPGShell exceptions."""


@dataclass
class UnexpectedStatusBaseError(GPGShellError):
    """Base for unexpected status error messages."""

    # The expected status line type
    expected_type: str

    # The expected status line arguments
    expected_args: dict[int, str]

    def __str__(self) -> str:
        args = " ".join(
            self.expected_args.get(i, "<anything>")
            for i in range(max(self.expected_args, default=-1) + 1)
        )
        if args:
            args += " "
        return f"Expected {self.expected_type} {args}..."


@dataclass
class UnexpectedEOFError(UnexpectedStatusBaseError):
    """
    Thrown when :py:meth:`GPGShell.expect_status` unexpectedly encounters the
    end of the stream.
    """

    def __str__(self) -> str:
        return f"Unexpected end of stream. {super().__str__()}"


@dataclass
class UnexpectedStatusError(UnexpectedStatusBaseError):
    """
    Thrown when :py:meth:`GPGShell.expect_status` encounters an unexpected
    status.
    """

    actual: StatusLine

    def __str__(self) -> str:
        return f"Unexpected status {self.actual}. {super().__str__()}"


@dataclass
class GPGShell:
    """
    Utility for interacting with with GnuPG in its machine-readable shell mode.
    """

    _status_stream: asyncio.StreamReader
    _command_stream: asyncio.StreamWriter | None

    # Any buffered line read from the stream but not yet processed. This may be
    # populated when we're attempting to read non-status-line values from the
    # stream.
    _buffered_line: str | None

    _log_file: TextIO | None

    def __init__(
        self,
        status_stream: asyncio.StreamReader,
        command_stream: asyncio.StreamWriter | None = None,
        log_file: TextIO | None = None,
    ) -> None:
        """
        Parameters
        ==========
        status_stream : asyncio.StreamReader
            The ``--status-fd`` pipe.
        command_stream : asyncio.StreamWriter
            The ``--command-fd`` pipe. If omitted, this shell will be
            read-only.
        log_file: TextIO or None
            If not None, the contents of the status_stream and command_stream
            will be duplicated into this log file.

            Note that lines may be read from the status_stream (and reflected
            in this log file) *before* they are interpreted by (e.g.)
            :py:meth:`read_status_line` or :py:meth:`read_non_status_line` due
            to internal read-ahead behaviour.
        """
        self._status_stream = status_stream
        self._command_stream = command_stream

        self._log_file = log_file

        self._buffered_line = None

    async def _readline(self) -> str:
        """Read a line of input, consuming the buffered line if present."""
        if self._buffered_line is not None:
            line = self._buffered_line
            self._buffered_line = None
        else:
            line = (await self._status_stream.readline()).decode()
            if self._log_file is not None:
                self._log_file.write(line)

        return line

    def _unreadline(self, line: str) -> None:
        """Un-read a line of input back into the line buffer."""
        assert self._buffered_line is None
        self._buffered_line = line

    async def read_status_line(self) -> StatusLine | None:
        """
        Low-level API. Read a status line from the stream. Reads None if the
        stream has ended.  Skips over non-status lines.
        """
        while True:
            line = await self._readline()

            if not line:
                return None
            elif line.startswith("[GNUPG:] "):
                type, _, args = (
                    line.removeprefix("[GNUPG:] ").removesuffix("\n").partition(" ")
                )
                return StatusLine(type, tuple(args.split(" ")) if args else ())
            else:
                # Skip non-status lines
                continue

    async def read_non_status_line(self) -> str | None:
        """
        Low level API. Read a single non-status ouput line from GnuPG. Returns
        None if no more status lines are available
        """
        line = await self._readline()

        if line.startswith("[GNUPG:] "):
            self._unreadline(line)
            return None
        elif line:
            return line
        else:
            return None

    async def read_non_status_lines(self) -> str | None:
        """
        Low-level API. Read all non-status ouput lines from GnuPG until either
        the next status line is received (which will remain buffered), or EOF.

        Returns a multi-line string or None if no more lines are available.
        """
        lines = ""
        while True:
            line = await self.read_non_status_line()
            if line is not None:
                lines += line
            elif not lines:
                return None
            else:
                return lines

    async def write_line(self, line: str) -> None:
        """
        Low-level API. Send a line to GnuPG. A terminating newline will be
        automatically added.
        """
        assert self._command_stream is not None
        self._command_stream.write(f"{line}\n".encode())
        if self._log_file is not None:
            self._log_file.write(f"{line}\n")
        await self._command_stream.drain()

    def _normalise_argument_constraints(
        self, *args: str, **kwargs: str
    ) -> dict[int, str]:
        """
        Given a set of constraint arguments (as accepted by
        :py:meth:`expect_status`) return a dictionary {arg_index:
        expected_value, ...}.
        """
        arg_constraints = {i: value for i, value in enumerate(args)}
        for name, value in kwargs.items():
            try:
                arg_constraints[int(name.removeprefix("arg_"))] = value
            except ValueError:
                raise TypeError("Keyword arguments must be of the form arg_N")
        return arg_constraints

    def _match_argument_constraints(
        self, status: StatusLine, type: str, arg_constraints: dict[int, str]
    ) -> bool:
        """
        Test whether the provided status line matches the specified
        constraints. Returns True iff it does.
        """
        if status.type != type:
            return False

        for i, value in arg_constraints.items():
            if i >= len(status.args) or status.args[i] != value:
                return False

        return True

    async def expect_status(self, type: str, *args: str, **kwargs: str) -> StatusLine:
        """
        Read the next status line and verify that it has the specified status
        type and arguments.

        Additional positional arguments are compared with the status line's
        corresponding arguments. Keyword arguments named ``arg_N`` where 'N' is
        a 0-indexed argument number can be used to constrain specific
        (non-contiguous) arguments.

        Throws an :py:exc:`UnexpectedStatusError` if the type or any provided
        arguments do not match the status line.
        """
        arg_constraints = self._normalise_argument_constraints(*args, **kwargs)

        # Check status matches expectations
        status = await self.read_status_line()
        if status is None:
            raise UnexpectedEOFError(type, arg_constraints)
        elif not self._match_argument_constraints(status, type, arg_constraints):
            raise UnexpectedStatusError(type, arg_constraints, status)

        return status

    async def skip_while_status(self, type: str, *args: str, **kwargs: str) -> None:
        """
        If the next status line matches the provided type and arguments,
        silently skip past it. Otherwise do nothing.

        See :py:meth:`expect_status` for argument details.
        """
        arg_constraints = self._normalise_argument_constraints(*args, **kwargs)

        while True:
            status = await self.read_status_line()
            if status is None:
                return
            elif self._match_argument_constraints(status, type, arg_constraints):
                # Skip past...
                continue
            else:
                # Line does not match, put it back in the buffer to be read
                # later...
                self._unreadline(
                    f"[GNUPG:] {status.type} {' '.join(status.args)}".rstrip() + "\n"
                )
                return

    async def send_command(self, command: str) -> None:
        """
        Send a command and wait for the ``GOT_IT`` response.
        """
        await self.write_line(command)
        await self.expect_status("GOT_IT")
