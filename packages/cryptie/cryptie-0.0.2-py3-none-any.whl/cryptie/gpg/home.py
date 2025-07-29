"""
Utilities for creating ephemeral GnuPG home environments.

Isolated GnuPG environments (homes) can be used independently of the user's own
GPG environment if any).  Further, using an isolated GnuPG environment allows
us to side-step all the usual complexities of managing trust in GnuPG: our
isolated environment only ever has a single key pair.

Isolated (and ephemeral) GnuPG environments are created by pointing the ``GNUPGHOME``
environment variable at an empty directory. The :py:func:`ephemeral_gpg_home`
context manager automates this process.
"""

import asyncio
import os
import stat
from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import AsyncIterator, TextIO

from cryptie.log_file_utils import log_command, record_stream


@asynccontextmanager
async def ephemeral_gpg_home(
    log_file: TextIO | None = None,
) -> AsyncIterator[Path]:
    """
    A context manager in which an ephemeral GnuPG environment ("home") is
    established.

    The context manager returns the Path of the ephemeral GnuPG home directory,
    though this is also set in the ``GNUPGHOME`` environment variable so GnuPG
    instances spawned within will use it automatically.

    Any running gpg-agents running in the ephemeral environment are killed
    automatically when the environment is cleaned up. This prevents them
    blocking access to any attached card.
    """
    gnupg_home_before = os.environ.get("GNUPGHOME", None)

    with TemporaryDirectory() as tmp_dir:
        gnupg_home = Path(tmp_dir) / "gnupg_home"
        gnupg_home.mkdir()
        gnupg_home.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)  # = 0700

        try:
            log_command(("export", f"GNUPGHOME={gnupg_home}"), log_file)
            os.environ["GNUPGHOME"] = str(gnupg_home)
            yield gnupg_home
        finally:
            try:
                await kill_gpg_agent(log_file)
            finally:
                # Restore original GNUPGHOME
                if gnupg_home_before is not None:
                    os.environ["GNUPGHOME"] = gnupg_home_before
                else:
                    del os.environ["GNUPGHOME"]


class KillGPGAgentError(Exception):
    """Thrown if we fail to kill the gpg-agent."""


async def kill_gpg_agent(log_file: TextIO | None = None) -> None:
    """
    Kill any running gpg-agent in the current GnuPG home using ``gpgconf --kill
    gpg-agent``.
    """
    cmd = (
        "gpgconf",
        "--kill",
        "gpg-agent",
    )
    log_command(cmd, log_file)
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert process.stdout is not None
    assert process.stderr is not None
    _stdout, stderr = await asyncio.gather(
        record_stream(process.stdout, log_file),
        record_stream(process.stderr, log_file),
    )
    await process.wait()
    if process.returncode != 0:
        raise KillGPGAgentError(stderr.rstrip())
