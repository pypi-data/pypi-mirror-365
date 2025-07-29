"""
This module contains an integration test of (non-card-based) GnuPG key
generation, export, import, encryption and decryption routines.
"""

import pytest

import sys
from pathlib import Path

from cryptie.gpg.home import ephemeral_gpg_home
from cryptie.gpg.keys import gpg_export, gpg_import, gpg_gen_key
from cryptie.gpg.cryptography import gpg_encrypt, gpg_decrypt


async def test_generate_encrypt_decrypt(tmp_path: Path) -> None:
    log_file = sys.stderr

    # Generate a keypair (without a passphrase)
    async with ephemeral_gpg_home(log_file):
        fingerprint = await gpg_gen_key("Test User", passphrase="", log_file=log_file)
        public_key = await gpg_export(fingerprint, public=True, log_file=log_file)
        private_key = await gpg_export(fingerprint, public=False, log_file=log_file)

    # Generate some dummy data
    plaintext_file = tmp_path / "plaintext"
    plaintext_file.write_text("Hello, world.")

    # Encrypt
    ciphertext_file = tmp_path / "ciphertext"
    with (
        plaintext_file.open("rb") as p,
        ciphertext_file.open("wb") as c,
    ):
        async with ephemeral_gpg_home(log_file):
            await gpg_encrypt(public_key.encode("ascii"), p, c, log_file)

    # Decrypt
    decrypted_file = tmp_path / "decrypted"
    with (
        ciphertext_file.open("rb") as c,
        decrypted_file.open("wb") as d,
    ):
        async with ephemeral_gpg_home(log_file):
            await gpg_import(private_key.encode("ascii"), log_file)
            await gpg_decrypt(c, d, log_file)

    # Verify
    assert decrypted_file.read_bytes() == plaintext_file.read_bytes()
