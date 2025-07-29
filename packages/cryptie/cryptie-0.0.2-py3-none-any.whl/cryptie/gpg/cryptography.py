"""
Wrappers around the encryption and decryption operaitons.

* Encrpting data (``gpg --encrypt``) :py:func:`gpg_encrypt`
* Decrypting data (``gpg --decrypt``) :py:func:`gpg_decrypt`
"""

import asyncio
from typing import BinaryIO, TextIO

from cryptie.gpg.keys import (
    KeyType,
    get_key_info,
    gpg_import,
)
from cryptie.log_file_utils import log_command, record_stream


class GPGEncryptError(Exception):
    """Thrown on gpg_encrypt failure."""


async def gpg_encrypt(
    public_key: bytes,
    plaintext: BinaryIO,
    ciphertext: BinaryIO,
    log_file: TextIO | None = None,
) -> None:
    """
    Encrypt the provided data using the provided public key. Reads from the
    plaintext file and writes to the ciphertext file.
    """
    # Load the key into GnuPG
    key_info = await get_key_info(public_key, log_file)
    if key_info.key_type != KeyType.public_key:
        raise ValueError("Expected a public, not private key!")

    await gpg_import(public_key, log_file)

    # Encrypt the data
    cmd = (
        "gpg",
        "--batch",
        "--no-tty",
        "--encrypt",
        # NB: Don't validate the freshly imported key with web of trust since
        # the imported key will initially be untrusted in the store...
        "--trust-model",
        "always",
        "--recipient",
        key_info.fingerprint,
    )
    log_command(cmd, log_file)
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=plaintext,
        stdout=ciphertext,
        stderr=asyncio.subprocess.PIPE,
    )

    assert process.stderr is not None
    stderr = await record_stream(process.stderr, log_file)

    await process.wait()
    if process.returncode != 0:
        raise GPGEncryptError(stderr.rstrip())


class GPGDecryptError(Exception):
    """Thrown on gpg_decrypt failure."""


async def gpg_decrypt(
    ciphertext: BinaryIO, plaintext: BinaryIO, log_file: TextIO | None = None
) -> None:
    """
    Decrypt the provided data using a private key already loaded into GnuPG.
    Reads from the ciphertext file and writes to the plaintext file.
    """
    # Decrypt the data
    cmd = (
        "gpg",
        "--batch",
        "--no-tty",
        "--decrypt",
    )
    log_command(cmd, log_file)
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=ciphertext,
        stdout=plaintext,
        stderr=asyncio.subprocess.PIPE,
    )

    assert process.stderr is not None
    stderr = await record_stream(process.stderr, log_file)

    await process.wait()
    if process.returncode != 0:
        raise GPGDecryptError(stderr.rstrip())
