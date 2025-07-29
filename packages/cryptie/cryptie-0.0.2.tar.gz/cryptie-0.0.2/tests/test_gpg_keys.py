import sys
from textwrap import dedent

from cryptie.gpg.home import ephemeral_gpg_home

from cryptie.gpg.keys import (
    KeyType,
    parse_key_info,
    gpg_gen_key,
    gpg_export,
    get_key_info,
)


class TestParseKeyInfo:
    def test_public_key(self) -> None:
        example_input = dedent(
            """
                pub:-:2048:1:027C34D46A6E7FB6:1719416149:::-:::scESCA::::::23::0:
                fpr:::::::::995A848E9169823AE25009FB027C34D46A6E7FB6:
                uid:-::::1719416149::2A215EF5D84E225B75EB3F779BECAD01A0446EF9::Foo Bar (comment) <foobar@example.com>::::::::::0:
                sub:-:2048:1:20657812390F3481:1719416149::::::a::::::23:
                fpr:::::::::491411FE377951532220A77820657812390F3481:
                sub:-:2048:1:0C9F3D0293267574:1719416149::::::e::::::23:
                fpr:::::::::3A629B6229C4598EF528B93B0C9F3D0293267574:
            """
        ).lstrip()

        data = parse_key_info(example_input, KeyType.public_key)

        # Should only have picked up the keys for the public key
        assert set(data) == {"pub", "fpr", "uid"}

        # Values should include all values (including the name again!)
        assert data["uid"][0] == "uid"
        assert data["uid"][9] == "Foo Bar (comment) <foobar@example.com>"

    def test_private_key(self) -> None:
        example_input = dedent(
            """
                sec:-:4096:1:9E115F049A8F43BD:1732029348:::-:::scESC::::::23::0:
                fpr:::::::::7A98561D1260CB15FE7362319E115F049A8F43BD:
                grp:::::::::9373ADBF9A48B289E013A13B88DBD1317269CFAB:
                uid:-::::1732029348::CA4B2A1850D05A20F0236130460694C49600DC67::Foo Bar::::::::::0:
                ssb:-:4096:1:27A9A7EB2125198F:1732029348::::::e::::::23:
                fpr:::::::::675E38FDBF690DFBDB2A3ED527A9A7EB2125198F:
                grp:::::::::656B36EDCD94C4335CC94FFB76B46D697E6E47A8:
            """
        ).lstrip()

        data = parse_key_info(example_input, KeyType.private_key)

        # Should only have picked up the keys for the public key
        assert set(data) == {"sec", "fpr", "grp", "uid"}

        # Values should include all values (including the name again!)
        assert data["uid"][0] == "uid"
        assert data["uid"][9] == "Foo Bar"


async def test_get_key_info() -> None:
    log_file = sys.stderr

    async with ephemeral_gpg_home(log_file):
        fingerprint = await gpg_gen_key("Test User", passphrase="", log_file=log_file)
        public_key = await gpg_export(fingerprint, public=True, log_file=log_file)
        private_key = await gpg_export(fingerprint, public=False, log_file=log_file)

    async with ephemeral_gpg_home(log_file):
        public_info = await get_key_info(public_key.encode("ascii"), log_file)
        private_info = await get_key_info(private_key.encode("ascii"), log_file)

    assert public_info.key_type == KeyType.public_key
    assert private_info.key_type == KeyType.private_key

    for info in [public_info, private_info]:
        assert info.user_id == "Test User"
        assert info.fingerprint == fingerprint
