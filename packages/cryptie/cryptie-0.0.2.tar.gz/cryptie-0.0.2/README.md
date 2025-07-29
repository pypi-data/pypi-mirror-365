Cryptie: Simple PGP-compatible public-key file encryption
=========================================================

This repository contains a simple tool for encrypting and decrypting files
using [OpenPGP-based](https://www.openpgp.org/) public key cryptography and
(optionally) [compatible 'smart
cards'](https://en.wikipedia.org/wiki/OpenPGP_card) (e.g.
[Yubikeys](https://www.yubico.com/products/yubikey-5-overview/)), without the
complexity of using PGP directly.

This tool is limited to the following simple operations:

* Creating key pairs on a PGP smart card or in software
* Encrypting data using a public key
* Decrypting data using private key (which may reside on a PGP smart card)

Nothing more, nothing less.

Whilst cryptie happens to use GnuPG/PGP internally, it *does not* attempt to be
a "simpler interface to all of PGP". Cryptie's primary use case is to provide a
secure, yet easy to use, way to perform PGP-compatible public key based
encryption and decryption. For example, you might use it to complement
[Hashicorp Vault's PGP unseal key encryption
feature](https://developer.hashicorp.com/vault/docs/concepts/pgp-gpg-keybase#initializing-with-gnupg).


Installation
------------

Cryptie can be installed directly from its repository using `pip`, e.g.:

    $ pip install cryptie

Cryptie relies on GnuPG to do what it needs to do.

**On Debian-alike-distributions:**

Install GnuPG and Smart Card Daemon (scdaemon) for Yubikey support:

    $ sudo apt install gnupg scdaemon

**On MacOS:**

Install GnuPG and the graphical `pinentry-mac` PIN entry tool:

    $ brew install gpg pinentry-mac

Add the following line to `/usr/local/etc/gnupg/gpg-agent.conf` (create it if
it doesn't exist):

    pinentry-program /usr/local/bin/pinentry-mac

This configures GnuPG to use the graphical `pinentry-mac` tool for obtaining
PINs (rather than the terminal, which may not be available e.g. within
Ansible).


Usage
-----

### Setting up PGP smart cards (e.g. Yubikey)

#### Generating keypairs on a PGP smart card

To generate a new keypair on a fresh smart card (e.g. Yubikey):

    $ cryptie init-card public_key.gpg "Your Name"

You will be prompted to enter the user PIN and admin PIN for the card several
times. 

> **Tip:** All PGP smart cards (including Yubikeys) are factory-programmed with
> a user PIN of 123456 and an admin PIN of 12345678.
>
> **Tip:** Yubikeys can be factory reset (permentantly deleting any private
> keys, and setting the PINs to default) using `ykman openpgp reset`.
>
> **Note:** PGP smart cards only have capacity for a single key pair.

The generated public key is written to `public_key.pgp` (in this example) and
the private key (irretrivably) resides in the smart card.

> **Warning:** The public key is *not* stored on the card and, if lost [is not
> easily
> recovered](https://lists.gnupg.org/pipermail/gnupg-users/2014-October/051051.html)
> and you will not be able to use the private key without it.


#### Changing PGP smart card PINs

You can (and should!) change the user and admin PINs from their defaults using:

    $ cryptie change-pin --user
    $ cryptie change-pin --admin

> **Tip:** The user PIN is needed whenever you wish to decrypt something. If
> you mistype it three times in a row, the card will become locked. It can be
> reset again using the admin PIN. The admin PIN is otherwise only used during
> card configuration.
>
> Since either PIN is enough to decrypt data (either directly or as a way to
> reset the user PIN), you should make sure both are chosen securely. You may
> choose to set both PINs to the same value.


### Setting up software-based keypairs

#### Generating keypairs in software

To generate a new keypair in software (i.e. not on a smart card):

    $ cryptie init-keypair public_key.gpg private_key.gpg "Your Name"

You will be prompted to enter a passphrase for the keypair several times.

#### Changing private key passphrases

To change the passphrase used to encrypt a software (i.e. non-smart card)
private key, use:

    $ cryptie change-passphrase private_key.gpg

You will be prompted to enter the old and new passphrases several times. By
default the private key file will be overwritten with the newly encrypted
private key.


### Encrypting data

You can encrypt some data with a public key like so (card not required):

    $ cryptie encrypt public_key.gpg < plaintext.txt > ciphertext.bin

You can decrypt the data again by providing the public key used to encrypt it
and inserting the card holding the private key:


### Decrypting data

To decrypt data using a private key held in a file (i.e. not on a smart card):

    $ cryptie decrypt private_key.gpg < ciphertext.bin > decrypted.txt

To decrypt data using a private key held on a PGP smart card (e.g. Yubikey):

    $ cryptie decrypt public_key.gpg < ciphertext.bin > decrypted.txt

> **Note:** The need to supply the public key is an unfortunate quirk of PGP
> and GnuPG.


### Showing metadata

In addition to the basic operations above, a pair of commands are also provided
for printing information about public keys and cards:

    $ cryptie card-info
    Card Serial: 12345678
    Key fingerprint: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

    $ cryptie key-info publick_key.gpg
    Type: public key
    User ID: John Doe (card serial 12345678) <john@example.com>
    Fingerprint: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    Key ID: BBBBBBBBBBBBBBBB

> **Tip:** By default, the card serial used to generate a keypair on a smart
> card is included in the user ID comment field.

For further details, see `--help`.


Troubleshooting card-not-found issues
-------------------------------------

If your card isn't being detected for some reason, it may be that some
component of GnuPG has got into a bad state and is holding onto the card. You
can use the following to try and unstick it.

Gracefully kill any running gpg-agent (this is usually done automatically by Cryptie).

    $ gpgconf --kill gpg-agent

In case there's some other gpg-agent in some long-lost GNUPGHOME still running,
you can use:

    $ killall gpg-agent

The card is actually interacted with via the scdaemon agent (controlled by
gpg-agent). Though this usually shuts down with gpg-agent, you can try killing
it manually:

    $ killall scdaemon

If you happen to have pcscd installed, this can also sometimes interfere with
card access. You can try restarting it to release control of any cards it has
grabbed.

    $ sudo systemctl restart pcscd


Troubleshooting other odd errors
--------------------------------

This tool acts as a wrapper around GnuPG. Whilst it only uses documented,
stable and explicitly machine-accessible interfaces, GnuPG is still primarily
designed as an interactive tool. As such, it is possible that changes to GnuPG
could cause issues to this tool.

Inserting `-vv` (two verbose flags) before the subcommand name will cause this
tool to print out every command it runs as well as displaying all GnuPG output.
This may help reveal what might be going on. In this mode, messages produced by
cryptie are prefixed with `###`.

Take a look at [`INTERNALS.md`](./INTERNALS.md) for a beginners overview of the
relevant parts of GnuPG and a description of what this tool does and how to
perform all of the necessary steps manually if needed. Likewise, see the
docstrings at the top of the files in the [`gpg` submodule](./cryptie/gpg/)
for more information.


Development
-----------

To run the test suite:

    $ pip install -r requirements-test.txt
    $ pytest
