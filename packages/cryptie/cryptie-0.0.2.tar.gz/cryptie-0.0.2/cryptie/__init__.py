import asyncio
import logging
import sys
from argparse import ArgumentParser, FileType, Namespace
from typing import TextIO

from cryptie.gpg import (
    PinChangeType,
    ephemeral_gpg_home,
    KeyType,
    get_key_info,
    gpg_card_status,
    gpg_change_pin,
    gpg_decrypt,
    gpg_encrypt,
    gpg_export,
    gpg_import,
    gpg_import_from_card,
    gpg_init_card,
    gpg_gen_key,
    gpg_change_passphrase,
    kill_gpg_agent,
)
from cryptie.gpg.card_edit import Algorithm

__version__ = "0.0.2"


logger = logging.getLogger(__name__)


async def init_card_command(args: Namespace, log_file: TextIO | None) -> None:
    """Implements the 'init-card' subcommand."""
    logger.info("Generating public/private keypair on PGP smart card.")
    if args.key_length > 2048:
        logger.info("Generating %d bit keys may take a few minutes.", args.key_length)
    logger.info("Please enter your PIN and Admin PIN when requested.")

    # Setup card with GPG
    card_info, fingerprint = await gpg_init_card(
        name=args.name,
        email=args.email,
        comment=args.comment,
        algo=Algorithm[args.algorithm],
        size=args.key_length,
        log_file=log_file,
    )
    logger.info("Keypair generated:")
    logger.info("  PGP smart card serial: %s", card_info.serial)
    logger.info("  Fingerprint: %s", fingerprint)

    # Store the public key
    public_key = await gpg_export(fingerprint, log_file=log_file)
    args.public_key.write(public_key)
    args.public_key.close()


async def init_keypair_command(args: Namespace, log_file: TextIO | None) -> None:
    """Implements the 'init-keypair' subcommand."""
    logger.info("Generating public/private keypair in software.")
    logger.info("Please enter a passphrase when requested.")

    fingerprint = await gpg_gen_key(
        name=args.name,
        size=args.key_length,
        log_file=log_file,
    )
    logger.info("Keypair generated:")
    logger.info("  Fingerprint: %s", fingerprint)

    # Store the public key
    public_key = await gpg_export(fingerprint, public=True, log_file=log_file)
    args.public_key.write(public_key)
    args.public_key.close()

    # Store the private key
    private_key = await gpg_export(fingerprint, public=False, log_file=log_file)
    args.private_key.write(private_key)
    args.private_key.close()


async def encrypt_command(args: Namespace, log_file: TextIO | None) -> None:
    """Implements the 'encrypt' subcommand."""
    public_key = args.public_key.read()
    logger.info("Encrypting data.")
    await gpg_encrypt(public_key, args.plaintext, args.ciphertext, log_file)
    args.ciphertext.close()


async def decrypt_command(args: Namespace, log_file: TextIO | None) -> None:
    """Implements the 'decrypt' subcommand."""
    key = args.key.read()

    key_info = await get_key_info(key, log_file)

    if key_info.key_type == KeyType.private_key:
        # Import the private key
        await gpg_import(key, log_file)
    elif key_info.key_type == KeyType.public_key:
        # Detect the matching ppg card
        logger.info("Identifying PGP smart card.")
        card_info, key_info = await gpg_import_from_card(key, log_file)

    # Decrypt the data
    logger.info("Decrypting data.")
    logger.info("Please enter PIN when requested.")
    await gpg_decrypt(args.ciphertext, args.plaintext, log_file)
    args.plaintext.close()


async def key_info_command(args: Namespace, log_file: TextIO | None) -> None:
    """Implements the 'key-info' subcommand."""
    public_key = args.public_key.read()

    key_info = await get_key_info(public_key, log_file)
    print(f"Type: {key_info.key_type.name.replace('_', ' ')}")
    print(f"User ID: {key_info.user_id}")
    print(f"Fingerprint: {key_info.fingerprint}")
    print(f"Key ID: {key_info.key_id}")


async def card_info_command(args: Namespace, log_file: TextIO | None) -> None:
    """Implements the 'card-info' subcommand."""
    card_info = await gpg_card_status(log_file)
    print(f"Card Serial: {card_info.serial}")
    if card_info.fingerprint is None:
        print("Key fingerprint: <no key found>")
    else:
        print(f"Key fingerprint: {card_info.fingerprint}")


async def change_pin_command(args: Namespace, log_file: TextIO | None) -> None:
    """Implements the 'change-pin' subcommand."""
    pin_change_type = args.pin_change_type
    logger.info("Please enter your old and new PIN when prompted.")
    await gpg_change_pin(pin_change_type, log_file)


async def change_passphrase_command(args: Namespace, log_file: TextIO | None) -> None:
    """Implements the 'change-passphrase' subcommand."""
    private_key = args.private_key.read()

    key_info = await get_key_info(private_key, log_file)
    if key_info.key_type != KeyType.private_key:
        raise ValueError("Expected a private, not public key.")

    logger.info("Please enter the old and new passphrase when prompted.")
    await gpg_import(private_key, log_file)
    await gpg_change_passphrase(key_info.fingerprint, log_file)
    new_private_key = await gpg_export(
        key_info.fingerprint, public=False, log_file=log_file
    )

    if args.new_private_key is not None:
        new_private_key_file = args.new_private_key
    else:
        new_private_key_file = args.private_key
        new_private_key_file.seek(0)
        new_private_key_file.truncate()
    new_private_key_file.write(new_private_key.encode("ascii"))


async def async_main() -> None:
    parser = ArgumentParser(
        description="""
            A utility for encrypting an decrypting files using public key
            cryptography and OpenPGP-compatible PGP smart cards (e.g. Yubikeys).
        """
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="""
            Increase verbosity. Use multiple times to increase verbosity
            further.
        """,
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=False,
        help="""
            Disable printing of informational messages.
        """,
    )
    parser.add_argument(
        "--no-kill-gpg-agent",
        action="store_true",
        default=False,
        help="""
            Do not shutdown running instances gpg-agent when running this
            script. (This done by default to avoid conflicts for PGP smart card
            access).
        """,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(title="command", required=True)

    init_card_parser = subparsers.add_parser(
        "init-card",
        help="""
            Intialise a PGP smart card (e.g. Yubikey) with a fresh
            private key, returning the corresponding public key.
        """,
    )
    init_card_parser.set_defaults(command=init_card_command)
    init_card_parser.add_argument(
        "public_key",
        type=FileType("w"),
        help="""
            The file to write the (ASCII Armored) generated public key to. Use
            '-' to write to stdout.
        """,
    )
    init_card_parser.add_argument(
        "name",
        type=str,
        help="""
            The full name of the owner of the key.
        """,
    )
    init_card_parser.add_argument(
        "--email",
        "-e",
        type=str,
        default="nobody@example.com",
        help="""
            The email address of the owner of the key. If omitted will default
            to %(default)s.
        """,
    )
    init_card_parser.add_argument(
        "--comment",
        "-c",
        type=str,
        default=None,
        help="""
            The comment to add to the name and email attached to the key. If
            omitted will default to a "card serial <number>" where <number> is
            the PGP smart card's serial number.
        """,
    )
    init_card_parser.add_argument(
        "--algorithm",
        "-a",
        default="RSA",
        choices=[a.name for a in Algorithm],
        help="""
            The type of key to generate. Defaults to %(default)s.
        """,
    )
    init_card_parser.add_argument(
        "--key-length",
        "-l",
        type=int,
        default=4096,
        help="""
            The length of key to generate in bits. Defaults to %(default)s.
        """,
    )

    init_keypair_parser = subparsers.add_parser(
        "init-keypair",
        help="""
            Generate a new (soft) PGP keypair on this computer (i.e. not on a
            PGP smart card or Yubikey).
        """,
    )
    init_keypair_parser.set_defaults(command=init_keypair_command)
    init_keypair_parser.add_argument(
        "public_key",
        type=FileType("w"),
        help="""
            The file to write the (ASCII Armored) generated public key to. Use
            '-' to write to stdout.
        """,
    )
    init_keypair_parser.add_argument(
        "private_key",
        type=FileType("w"),
        help="""
            The file to write the (ASCII Armored) generated private key to. Use
            '-' to write to stdout.
        """,
    )
    init_keypair_parser.add_argument(
        "name",
        type=str,
        help="""
            The full name of the owner of the key.
        """,
    )
    init_keypair_parser.add_argument(
        "--key-length",
        "-l",
        type=int,
        default=4096,
        help="""
            The length of the RSA key to generate in bits. Defaults to %(default)s.
        """,
    )

    encrypt_parser = subparsers.add_parser(
        "encrypt",
        help="""
            Encrypt a file using a specified public key.
        """,
    )
    encrypt_parser.set_defaults(command=encrypt_command)
    encrypt_parser.add_argument(
        "public_key",
        type=FileType("rb"),
        help="""
            The filename of a file containing the GnuPG public key to use to
            encrypt the file. Use '-' to read from stdin.
        """,
    )
    encrypt_parser.add_argument(
        "plaintext",
        nargs="?",
        type=FileType("rb"),
        default=sys.stdin.buffer,
        help="""
            The file to be encrypted. If omitted, or set to '-', standard input
            will be used.
        """,
    )
    encrypt_parser.add_argument(
        "--ciphertext",
        "--output",
        "-o",
        type=FileType("wb"),
        default=sys.stdout.buffer,
        help="""
            The file to write the encrypted data to. By default, or if '-' is
            specified, writes to stdout.
        """,
    )

    decrypt_parser = subparsers.add_parser(
        "decrypt",
        help="""
            Decrypt a file using a private key stored in a file or held on a
            PGP smart card (e.g.  Yubikey).
        """,
    )
    decrypt_parser.set_defaults(command=decrypt_command)
    decrypt_parser.add_argument(
        "key",
        type=FileType("rb"),
        help="""
            The filename of the private key to use to decrypt the data.  If
            decrypting using a card (e.g. yubikey), this argument should
            instead be the filename of the matching *public* key for the
            inserted card.  Use '-' to read from stdin.
        """,
    )
    decrypt_parser.add_argument(
        "ciphertext",
        nargs="?",
        type=FileType("rb"),
        default=sys.stdin.buffer,
        help="""
            The file to be decrypted. If omitted, or set to '-', standard input
            will be used.
        """,
    )
    decrypt_parser.add_argument(
        "--plaintext",
        "--output",
        "-o",
        type=FileType("wb"),
        default=sys.stdout.buffer,
        help="""
            The file to write the decrypted plaintext data to. By default, or if '-' is
            specified, writes to stdout.
        """,
    )

    key_info_parser = subparsers.add_parser(
        "key-info",
        help="""
            Show basic information about a public key.
        """,
    )
    key_info_parser.set_defaults(command=key_info_command)
    key_info_parser.add_argument(
        "public_key",
        type=FileType("rb"),
        help="""
            The filename of a public key. Use '-' to read from stdin.
        """,
    )

    card_info_parser = subparsers.add_parser(
        "card-info",
        help="""
            Show basic information about the inserted card (e.g. Yubikey).
        """,
    )
    card_info_parser.set_defaults(command=card_info_command)

    change_pin_parser = subparsers.add_parser(
        "change-pin",
        help="""
            Change a card's PIN
        """,
    )
    change_pin_parser.set_defaults(command=change_pin_command)
    pin_change_type_group = change_pin_parser.add_mutually_exclusive_group(
        required=True
    )
    pin_change_type_group.add_argument(
        "--user",
        "-u",
        action="store_const",
        dest="pin_change_type",
        const=PinChangeType.user_pin,
        help="""
            Change the user PIN.
        """,
    )
    pin_change_type_group.add_argument(
        "--reset-user",
        "-r",
        action="store_const",
        dest="pin_change_type",
        const=PinChangeType.unblock_pin,
        help="""
            Reset the user PIN using the admin PIN.
        """,
    )
    pin_change_type_group.add_argument(
        "--admin",
        "-a",
        action="store_const",
        dest="pin_change_type",
        const=PinChangeType.admin_pin,
        help="""
            Change the admin PIN.
        """,
    )

    change_passphrase_parser = subparsers.add_parser(
        "change-passphrase",
        help="""
            Change a private key's passphrase
        """,
    )
    change_passphrase_parser.set_defaults(command=change_passphrase_command)
    change_passphrase_parser.add_argument(
        "private_key",
        type=FileType("r+b"),
        help="""
            The filename of the file containing the private key whose
            passphrase is to be changed.
        """,
    )
    change_passphrase_parser.add_argument(
        "new_private_key",
        type=FileType("wb"),
        default=None,
        nargs="?",
        help="""
            The filename of the file to write the private key with the new
            passphrase to. If not specified, the original private key file will
            be edited in place.
        """,
    )

    args = parser.parse_args()

    # Control output verbosity
    log_file = None
    hide_traceback_for_local_exceptions = True
    log_level = logging.INFO
    log_format = "%(message)s"
    if args.quiet:
        log_level = logging.ERROR
    if args.verbose >= 1:
        log_level = logging.DEBUG
        hide_traceback_for_local_exceptions = False
    if args.verbose >= 2:
        log_format = "### %(message)s"
        log_file = sys.stderr

    logging.basicConfig(level=log_level, format=log_format)

    try:
        # Kill any GnuPG agent the user may have running to prevent it blocking
        # access to the PGP smart card
        if not args.no_kill_gpg_agent:
            await kill_gpg_agent(log_file)

        # Act on the command within an ephemeral, isolated GnuPG home
        async with ephemeral_gpg_home(log_file):
            await args.command(args, log_file)
    except Exception as exc:
        this_package = __name__.partition(".")[0]
        exc_package = type(exc).__module__.partition(".")[0]
        local_exception = this_package == exc_package
        if hide_traceback_for_local_exceptions and local_exception:
            print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
            sys.exit(1)
        else:
            raise


def main() -> None:
    asyncio.run(async_main())
