"""
This module provides a wrapper for ``gpg --card-status``,
:py:func:`gpg_card_status`.
"""

import asyncio
from dataclasses import dataclass
from typing import NamedTuple, TextIO

from cryptie.gpg.shell import GPGShell, StatusLine
from cryptie.log_file_utils import log_command, record_stream


class CardInfo(NamedTuple):
    """
    (Subset of) the basic card information reported by GPG's --card-edit
    command.
    """

    serial: str
    fingerprint: str | None  # None if the card doesn't have any keys


@dataclass
class CardDetectionError(Exception):
    """
    Thrown when the GPG card is not detected in a good state.
    """

    what: str  # The "what" argument from the CARDCTRL command.

    def __str__(self) -> str:
        if self.what == "1":
            return "Card must be inserted"
        elif self.what == "2":
            return "Card must be removed"
        elif self.what == "4":
            return "No card available"
        elif self.what == "5":
            return "No card reader available"
        elif self.what == "6":
            return "No card support available"
        elif self.what == "7":
            return "Card is in termination state"
        else:
            return "Unknown CARDCTRL code '{self.what}'"


async def expect_cardctrl(shell: GPGShell) -> StatusLine:
    """
    Verify that we have received a 'CARDCTRL 3' status from the shell (i.e.
    card found), throwing a CardDetectionError if not found.
    """
    status = await shell.expect_status("CARDCTRL")

    if status.args[0] != "3":  # 3 = "Card with serial number detected"
        raise CardDetectionError(status.args[0])

    return status


def parse_card_status(lines: str) -> CardInfo:
    """
    Parses the colon-delimited (non-status-line) output of ``--card-status`` or
    initial output of ``--card-edit``.
    """
    # Parse colon-delimited data
    card_details = {
        line.partition(":")[0]: line.split(":") for line in lines.splitlines()
    }

    return CardInfo(
        serial=card_details["serial"][1],
        fingerprint=card_details["fpr"][1] or None,
    )


async def expect_cardctrl_with_card_info(shell: GPGShell) -> CardInfo:
    """
    Verify that we've receieved a "CARDCTRL 3" status line (i.e. a card was
    found) and return the parsed card information printed afterwards.
    """
    await expect_cardctrl(shell)
    return parse_card_status((await shell.read_non_status_lines()) or "")


class GPGCardStatusError(Exception):
    """Thrown if gpg_card_status fails."""


async def gpg_card_status(log_file: TextIO | None = None) -> CardInfo:
    """
    Make GnuPG detect the attached smart card (runs ``gpg --card-status``).

    This has the side-effect of matching up the private key on the card with
    any installed public key.
    """
    cmd = (
        "gpg",
        "--batch",
        "--no-tty",
        "--with-colons",  # Machine readable output
        "--status-fd=1",  # Machine readable status
        "--card-status",
    )
    log_command(cmd, log_file)
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert process.stdout is not None
    assert process.stderr is not None
    info, stderr = await asyncio.gather(
        expect_cardctrl_with_card_info(GPGShell(process.stdout, log_file=log_file)),
        record_stream(process.stderr, log_file),
    )
    await process.wait()
    if process.returncode != 0:
        raise GPGCardStatusError(stderr.rstrip())

    return info
