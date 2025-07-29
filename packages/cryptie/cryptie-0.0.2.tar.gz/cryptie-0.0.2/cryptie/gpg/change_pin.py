"""
A wrapper around the gpg `--change-pin` command, :py:func:`gpg_change_pin`.
"""

import asyncio
from enum import Enum
from typing import TextIO

from cryptie.gpg.card_edit import PinEntryError
from cryptie.gpg.card_status import expect_cardctrl
from cryptie.gpg.shell import GPGShell, UnexpectedStatusError
from cryptie.log_file_utils import log_command, record_stream


class PinChangeType(Enum):
    # Change the user PIN
    user_pin = "1"

    # Use the Admin PIN to reset the user PIN
    unblock_pin = "2"

    # Change the Admin PIN
    admin_pin = "3"


class PinChangeError(Exception):
    """Thrown when gpg_change_pin fails."""


async def gpg_change_pin(
    pin_type: PinChangeType,
    log_file: TextIO | None = None,
) -> None:
    """
    Change the PIN of a smart card using ``gpg --change-pin``.

    During execution, various PIN requests will be made via pinentry.
    """
    cmd = (
        "gpg",
        "--no-tty",  # Send all messages to stderr, not the TTY
        "--with-colons",  # Enable machine-parsable interface
        "--command-fd=0",  # Input on stdin
        "--status-fd=1",  # Output on stdout
        "--expert",  # Ask everything...
        "--change-pin",
    )
    log_command(cmd, log_file)
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    assert process.stderr is not None
    stderr_logger = asyncio.create_task(record_stream(process.stderr, log_file))

    assert process.stdout is not None
    assert process.stdin is not None
    shell = GPGShell(process.stdout, process.stdin, log_file)

    try:
        # Check card is found
        await expect_cardctrl(shell)

        # Request pin change
        await shell.expect_status("GET_LINE", "cardutil.change_pin.menu")
        await shell.send_command(pin_type.value)
        await shell.skip_while_status("PINENTRY_LAUNCHED")

        # Check successful PIN entry
        try:
            await shell.expect_status("SC_OP_SUCCESS")
        except UnexpectedStatusError as exc:
            if exc.actual.type == "SC_OP_FAILURE" and exc.actual.args:
                raise PinEntryError(exc.actual.args[0])
            elif exc.actual.type == "SC_OP_FAILURE":
                min_length = 8 if pin_type == PinChangeType.admin_pin else 6
                raise PinChangeError(
                    f"Couldn't change the PIN.\n"
                    f"Hint: Was the pin at least {min_length} characters?"
                )
            else:
                raise

        # Quit
        await shell.expect_status("GET_LINE", "cardutil.change_pin.menu")
        await shell.send_command("q")
    except:
        if process.returncode is None:
            process.kill()
        raise
    finally:
        await process.wait()
        await stderr_logger
