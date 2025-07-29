"""
Utilities for importing and exporting keys from a GnuPG trust store.

The key parts are

* :py:func:`gpg_export` -- Export a public key using ``gpg --export``.
* :py:func:`gpg_import` -- Import a public key using ``gpg --import``.
* :py:func:`gpg_import_from_card` -- Import a public key and corresponding
  private key residing on a PGP card using ``gpg --import`` and ``gpg
  --card-status``.
* :py:func:`parse_public_key_info` -- Extract metadata from an exported public
  key file.

"""

import asyncio
from dataclasses import dataclass
from typing import NamedTuple, TextIO
from enum import Enum

from cryptie.gpg.card_status import CardInfo, gpg_card_status
from cryptie.log_file_utils import log_command, record_stream
from cryptie.gpg.shell import GPGShell


class GPGExportError(Exception):
    """Thrown on gpg_export failing."""


async def gpg_export(
    fingerprint: str,
    public: bool = True,
    log_file: TextIO | None = None,
) -> str:
    """
    Exports the specified key from GPG. Returns the ASCII armoured GPG key.

    Exports the public key if 'public' is True, otherwise exports the private
    key.
    """

    cmd = (
        "gpg",
        "--batch",
        "--no-tty",
        "--armor",
        "--export" if public else "--export-secret-key",
        fingerprint,
    )
    log_command(cmd, log_file)
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if log_file is not None:
        log_file.write(stderr.decode())

    if process.returncode != 0:
        raise GPGExportError(stderr.rstrip())

    return stdout.decode("ascii")


class GPGImportError(Exception):
    """Thrown on gpg_import failure."""


async def gpg_import(key: bytes, log_file: TextIO | None = None) -> None:
    """
    Import a provided (binary or ASCII Armored) key into GnuPG.
    """
    cmd = (
        "gpg",
        "--batch",
        "--no-tty",
        "--import",
    )
    log_command(cmd, log_file)
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert process.stdin is not None
    process.stdin.write(key)
    process.stdin.close()

    assert process.stdout is not None
    assert process.stderr is not None
    _stdout, stderr = await asyncio.gather(
        record_stream(process.stdout, log_file),
        record_stream(process.stderr, log_file),
    )
    await process.wait()
    if process.returncode != 0:
        raise GPGImportError(stderr.rstrip())


class KeyType(Enum):
    private_key = "sec"
    public_key = "pub"


def parse_key_info(
    colon_data: str, key_type: KeyType = KeyType.public_key
) -> dict[str, list[str]]:
    """
    Given a set of colon-delimited data from ``gpg --import-mode-show-only
    --import --with-colons``, return the data fields for the contained public
    key only.

    Returns a dictionary mapping from type field (column 0) to a list
    containing all of the column values for that type (beginning with the type
    name again in index 0!).

    See the GnuPG `DETAILS`_ documentation for more information on the format.

    .. DETAILS: https://github.com/gpg/gnupg/blob/master/doc/DETAILS
    """
    data = {}

    reached_target_key = False
    for line in colon_data.splitlines():
        columns = line.split(":")

        # Read only entries related to the first public key listed, stopping as
        # soon as we encounter any subkeys etc.
        if not reached_target_key and columns[0] == key_type.value:
            reached_target_key = True
        elif reached_target_key and columns[0] in (
            "pub",
            "crt",
            "crs",
            "sub",
            "sec",
            "ssb",
        ):
            break

        if reached_target_key:
            assert columns[0] not in data
            data[columns[0]] = columns

    return data


class KeyInfo(NamedTuple):
    key_type: KeyType
    key_id: str
    fingerprint: str
    user_id: str


async def get_key_info(key: bytes, log_file: TextIO | None = None) -> KeyInfo:
    """
    Return basic GnuPG public or private key info for the first public or
    private key stored in the provided GPG key data. If the data contains both
    public and private keys, returns information about the private key.
    """
    cmd = (
        "gpg",
        "--batch",
        "--no-tty",
        "--with-colons",  # Machine-readable output
        "--import-options",  # Don't actually import, just print the contents
        "show-only",
        "--import",
    )
    log_command(cmd, log_file)
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert process.stdin is not None
    process.stdin.write(key)
    process.stdin.close()

    assert process.stdout is not None
    assert process.stderr is not None
    stdout, stderr = await asyncio.gather(
        record_stream(process.stdout, log_file),
        record_stream(process.stderr, log_file),
    )
    await process.wait()

    if process.returncode != 0:
        raise GPGImportError(stderr.rstrip())

    # Look for first public/private key
    #
    # See the GnuPG "DETAILS" documentation for column definitions!
    # https://github.com/gpg/gnupg/blob/master/doc/DETAILS
    for key_type in KeyType:
        data = parse_key_info(stdout, key_type)
        if data:
            break
    else:
        raise ValueError("No public or private key present.")

    return KeyInfo(
        key_type=key_type,
        key_id=data[key_type.value][4],
        # XXX: We don't perform escaping for these fields, but hopefully they
        # won't contain anything worth escaping (e.g. colons!)!
        fingerprint=data["fpr"][9],
        user_id=data["uid"][9],
    )


@dataclass
class GPGImportFromCardError(Exception):
    """Thrown on failure of gpg_import_from_card."""

    card_info: CardInfo
    key_info: KeyInfo

    def __str__(self) -> str:
        if (
            # The user ID looks like it contains the serial number in the
            # comment (which placed there by default by this tool)
            "(card serial " in self.key_info.user_id
            and
            # But the attached card's serial doesn't appear to be there
            self.card_info.serial not in self.key_info.user_id
        ):
            hint = "Hint: This might not be the right card for the public key provided."
        elif self.card_info.serial in self.key_info.user_id:
            hint = "Hint: Might this card have been reset since this public key was generated?"
        else:
            hint = ""

        return (
            f"Public key does not match private key stored on card.\n"
            f"  Public key user ID: {self.key_info.user_id}\n"
            f"  Public key fingerprint: {self.key_info.fingerprint}\n"
            f"  Card key fingerprint: {self.card_info.fingerprint}\n"
            f"  Card Serial: {self.card_info.serial}\n"
            f"{hint}\n"
        ).rstrip()


async def gpg_import_from_card(
    public_key: bytes, log_file: TextIO | None = None
) -> tuple[CardInfo, KeyInfo]:
    """
    Cause GnuPG to discover a PGP private key matching the provided public key
    on an inserted smart card.
    """
    # Insert public key into trust store (GnuPG won't detect the card without
    # having done this first).
    await gpg_import(public_key, log_file)

    # Have GnuPG detect the card
    card_info = await gpg_card_status(log_file)

    # Test to see whether the public key we've been given and the private key
    # on the card match. If they do, GnpPG should have notionally added the
    # private key to its trust store as a side effect of running
    # gpg_card_status above. If they don't, this won't have happend so we
    # should complain at this point!
    key_info = await get_key_info(public_key, log_file)
    if key_info.key_type != KeyType.public_key:
        raise ValueError("Expected a public, not private key.")
    if key_info.fingerprint != card_info.fingerprint:
        raise GPGImportFromCardError(card_info, key_info)

    return card_info, key_info


class GPGGenKeyError(Exception):
    """Thrown on gpg_gen_key failure."""


async def gpg_gen_key(
    name: str,
    size: int = 4096,
    passphrase: str | None = None,
    log_file: TextIO | None = None,
) -> str:
    """
    Generate an RSA key pair with the specified number of bits. Returns the
    fingerprint.

    The 'passphrase' argument is intended for use during testing and allows the
    desired passphrase (which may be "") to be selected without interactively
    prompting the user. Note that for anything other than an empty passphrase,
    GnuPG will still prompt you for the chosen passphrase interactively to
    generate the subkey(!)
    """
    cmd: tuple[str, ...] = (
        "gpg",
        "--batch",  # Don't ask any questions
        "--yes",  # Overwrite an existing key with the same name
        "--no-tty",  # Send all messages to stderr, not the TTY
        "--with-colons",  # Enable machine-parsable interface
        "--status-fd=1",  # Output on stdout
        "--expert",  # Ask everything...
    )

    if passphrase is not None:
        cmd += (
            "--pinentry-mode=loopback",
            "--passphrase-fd=0",  # stdin
        )

    cmd += (
        # Specify the algorithm to use. Note we have to specify this here
        # (rather than in the 'algorithm' argument for --quick-gen-key) because
        # otherwise a subkey is not generated rendering the keypair useless.
        "--default-new-key-algo",
        f"rsa{size}/cert,sign+rsa{size}/encr",
        # Trigger simple key generation
        "--quick-gen-key",
        name,  # Key owner's name
        "default",  # Algorithm (need to set default to generate subkey)
        "default",  # Usage
        "0",  # Expiration (0 = never)
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
    shell = GPGShell(process.stdout, log_file=log_file)

    try:
        # Supply passphrase (if specified)
        assert process.stdin is not None
        if passphrase is not None:
            process.stdin.write(passphrase.encode("utf-8"))
        process.stdin.close()

        # Use may be asked for passphrases, ignore this
        await shell.skip_while_status("PINENTRY_LAUNCHED")

        # Ignore key generation status
        await shell.skip_while_status("KEY_CONSIDERED")

        # Get the key fingerprint
        fingerprint = (await shell.expect_status("KEY_CREATED")).args[1]

        await process.wait()
        if process.returncode != 0:
            raise GPGGenKeyError(await stderr_logger)

        return fingerprint
    except:
        if process.returncode is None:
            process.kill()
        raise
    finally:
        await process.wait()
        await stderr_logger


class GPGChangePassphraseError(Exception):
    """Thrown on gpg_change_passphrase failure."""


async def gpg_change_passphrase(
    fingerprint: str,
    log_file: TextIO | None = None,
) -> None:
    """
    Change a private key's passphrase.
    """
    cmd: tuple[str, ...] = (
        "gpg",
        "--batch",  # Don't ask any questions
        "--no-tty",  # Send all messages to stderr, not the TTY
        "--with-colons",  # Enable machine-parsable interface
        "--status-fd=1",  # Output on stdout
        "--change-passphrase",
        fingerprint,
    )

    log_command(cmd, log_file)
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    assert process.stderr is not None
    stderr_logger = asyncio.create_task(record_stream(process.stderr, log_file))

    assert process.stdout is not None
    shell = GPGShell(process.stdout, log_file=log_file)

    try:
        await shell.skip_while_status("KEY_CONSIDERED")
        await shell.skip_while_status("PINENTRY_LAUNCHED")
        await shell.expect_status("SUCCESS")

        await process.wait()
        if process.returncode != 0:
            raise GPGChangePassphraseError(await stderr_logger)
    except:
        if process.returncode is None:
            process.kill()
        raise
    finally:
        await process.wait()
        await stderr_logger
