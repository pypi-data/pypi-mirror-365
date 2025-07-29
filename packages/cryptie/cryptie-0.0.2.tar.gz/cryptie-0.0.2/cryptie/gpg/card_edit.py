"""
This module includes the automations for initialising a PGP private and public
key within a card using gpg's ``gpg --card-edit`` shell.

The :py:func:`gpg_init_card` wraps this entire process in a simple-to-use
function.

Operating the ``--card-edit`` shell to initialise a card boils down to the
following sequence of commands and answering the provided questions in the
obvious way (based on the process outlined in the `Yubikey Docs`_):

* ``admin`` -- Enable administrative commands
* ``key-attr`` -- Choosing the key type and size
* ``generate`` -- Generating the public/private key pair on the device
* ``quit`` -- Generating the public/private key pair on the device

.. Yubikey Docs: https://support.yubico.com/hc/en-us/articles/360013790259-Using-Your-YubiKey-with-OpenPGP

The various ``card_edit_*`` functions automate calling of the commands
enumerated above, filling out any requred details.
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import TextIO

import logging

from cryptie.gpg.card_status import CardInfo, expect_cardctrl_with_card_info
from cryptie.gpg.shell import GPGShell, UnexpectedStatusError
from cryptie.log_file_utils import log_command, record_stream


logger = logging.getLogger(__name__)


class CardEditError(Exception):
    """Base class for errors relating to --card-edit commands."""


async def card_edit_admin(shell: GPGShell) -> None:
    """Enable admin commands in the ``--card-edit`` shell."""
    await shell.expect_status("GET_LINE", "cardedit.prompt")
    await shell.send_command("admin")


class Algorithm(Enum):
    RSA = "1"
    ECC = "2"


async def card_edit_key_attr(
    shell: GPGShell,
    algo: Algorithm = Algorithm.RSA,
    size: int = 2048,
) -> None:
    """
    Set the key type and size to use on PGP card.

    Sets the same options for all three keys (signing, encryption and
    authentication).
    """
    await shell.expect_status("GET_LINE", "cardedit.prompt")
    await shell.send_command("key-attr")

    # Set all three keys to the same type/size
    key_types = ["signing", "encryption", "authentication"]
    for i, _key_type in enumerate(key_types):
        logger.info(f"Setting card key size ({i+1} of {len(key_types)})")
        await shell.expect_status("GET_LINE", "cardedit.genkeys.algo")
        await shell.send_command(algo.value)
        await shell.expect_status("GET_LINE", "cardedit.genkeys.size")
        await shell.send_command(str(size))
        await shell.skip_while_status("PINENTRY_LAUNCHED")


@dataclass
class PinEntryError(CardEditError):
    """Error when requesting PIN."""

    code: str

    def __str__(self) -> str:
        if self.code == "1":
            return "PIN entry cancelled"
        elif self.code == "2":
            return "Incorrect PIN"
        else:
            return f"PIN entry error code {self.code}"


@dataclass
class KeyAlreadyPresentError(CardEditError):
    def __str__(self) -> str:
        return (
            "A PGP private key already exists on this device.\n"
            "Hint: To reset the device (permenantly deleting any existing key), run:\n"
            "  $ ykman openpgp reset"
        )


async def card_edit_generate(
    shell: GPGShell,
    name: str,
    email: str,
    comment: str,
) -> str:
    """
    Generate a new public/private key pair entirely on the device.

    Returns the hex fingerprint of the generated "signing" private key.
    """
    try:
        await shell.expect_status("GET_LINE", "cardedit.prompt")
        await shell.send_command("generate")

        # Don't create key backup
        await shell.expect_status("GET_LINE", "cardedit.genkeys.backup_enc")
        await shell.send_command("n")  # n = No

        # GnuPG internally changes the PIN entry policy to non-forced mode so
        # that during generation the PIN is not requested for each of the
        # several keypairs generated. The PIN is pre-emptively requested after
        # this setting change.
        #
        # (See the check_pin_for_key_operation function in GnuPG.)
        logger.info("Preparing to generate key pair...")
        await shell.skip_while_status("PINENTRY_LAUNCHED")  # User PIN

        # Make a non-expiring key
        await shell.expect_status("GET_LINE", "keygen.valid")
        await shell.send_command("0")  # 0 = Never expires

        # Enter personal details
        await shell.expect_status("GET_LINE", "keygen.name")
        await shell.send_command(name)

        await shell.expect_status("GET_LINE", "keygen.email")
        await shell.send_command(email)

        await shell.expect_status("GET_LINE", "keygen.comment")
        await shell.send_command(comment)

        # It is at this point we actually trigger keypair generation.
        logger.info("Beginning keypair generation on card...")
        await shell.skip_while_status("PINENTRY_LAUNCHED")  # Admin PIN
        logger.info("Continuing keypair generation on card...")
        await shell.skip_while_status("PINENTRY_LAUNCHED")  # User PIN

        # Wait for key to be generated
        await shell.expect_status("KEY_CONSIDERED")
        await shell.expect_status("KEY_CONSIDERED")

        # B = Both
        fingerprint = (await shell.expect_status("KEY_CREATED", "B")).args[1]

        return fingerprint
    except UnexpectedStatusError as exc:
        if exc.actual.type == "SC_OP_FAILURE":
            raise PinEntryError(exc.actual.args[0])
        elif (
            exc.actual.type == "GET_BOOL"
            and exc.actual.args[0] == "cardedit.genkeys.replace_keys"
        ):
            raise KeyAlreadyPresentError()
        else:
            raise


async def card_edit_quit(shell: GPGShell) -> None:
    """Quit the card-edit shell."""
    await shell.expect_status("GET_LINE", "cardedit.prompt")
    await shell.send_command("quit")


async def gpg_init_card(
    name: str,
    email: str,
    comment: str | None = None,
    algo: Algorithm = Algorithm.RSA,
    size: int = 2048,
    log_file: TextIO | None = None,
) -> tuple[CardInfo, str]:
    """
    Initialise a new card with an on-card generated private/public key pair
    using the ``gpg --card-edit`` ``generate`` command.

    Returns card information and the fingerprint of the generated private key.

    During execution, various PIN requests may be made via pinentry.

    If 'comment' is set to None, the comment will be set to "card serial <card
    serial here>".
    """
    cmd = (
        "gpg",
        "--no-tty",  # Send all messages to stderr, not the TTY
        "--with-colons",  # Enable machine-parsable interface
        "--command-fd=0",  # Input on stdin
        "--status-fd=1",  # Output on stdout
        "--expert",  # Ask everything...
        "--card-edit",
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
        # Get card information (and check one is found!)
        card_info = await expect_cardctrl_with_card_info(shell)
        if comment is None:
            comment = f"card serial {card_info.serial}"

        # Remaining commands are admin commands, enable them
        await card_edit_admin(shell)

        # Set key type/size
        await card_edit_key_attr(shell, algo=algo, size=size)

        # Generate a key
        fingerprint = await card_edit_generate(shell, name, email, comment)

        # Exit
        await card_edit_quit(shell)
        await process.wait()
        if process.returncode != 0:
            raise CardEditError(await stderr_logger)

        return card_info, fingerprint
    except:
        if process.returncode is None:
            process.kill()
        raise
    finally:
        await process.wait()
        await stderr_logger
