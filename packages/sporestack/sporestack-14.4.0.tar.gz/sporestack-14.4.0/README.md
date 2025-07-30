# Python 3 library and CLI for [SporeStack](https://sporestack.com) ([SporeStack Tor Hidden Service](http://spore64i5sofqlfz5gq2ju4msgzojjwifls7rok2cti624zyq3fcelad.onion))

[Changelog](CHANGELOG.md)

## Requirements

* Python 3.9-3.11 (and likely newer)

## Running without installing

* Make sure [pipx](https://pipx.pypya.io) is installed.
* `pipx run 'sporestack[cli]'`

## Installation with pipx

* Make sure [pipx](https://pipx.pypya.io) is installed.
* `pipx install 'sporestack[cli]'`

## Traditional installation

* Recommended: Create and activate a virtual environment, first.
* `pip install sporestack` (Run `pip install 'sporestack[cli]'` if you wish to use the command line `sporestack` functionality and not just the Python library.)

## Getting started

Recommended: Make sure you're on the latest stable version comparing `sporestack version` with git tags in this repository, or releases on [PyPI](https://pypi.org/project/sporestack/).

* `sporestack aup`

First, read the Acceptable Use Policy.

* `sporestack token create --dollars 250 --currency xmr`

Create a new token. Fund it with $250, and pay with Monero.

This command will suggest that you create an SSH key for the token. That command should look something like this...

* `ssh-keygen -C "" -t ed25519 -f ~/.sporestack/sshkey/primary/id_ed25519'`

We recommend creating an SSH key for your token. If you don't want do this, you can pass `--ssh-key-file` when you launch a server. Otherwise, `~/.ssh/id_rsa.pub` will be the default.

This SSH key should be backed up and kept secret, just like your token!

## Usage examples

* `sporestack token list`

List the tokens that you have saved locally.

* `sporestack token info`

View information about the token, including how many days left your token can sustain your autorenewal servers for.

* `sporestack token messages`

View messages on the token.

* `sporestack token invoices`

View invoices on the token.

* `sporestack server operating-systems`

View available operating systems.

* `sporestack server flavors`

View available "flavors" (plans, or server sizes.)

* `sporestack server regions`

View available regions. Note that all three of these commands accept a `--provider` option, in case you're only interested in viewing a particular provider's servers.

* `sporestack server launch --hostname SomeHostname --operating-system freebsd-14 --autorenew --provider vultr --flavor vc2-1c-1gb --region ord`

Launch a FreeBSD 14 server on Vultr, in Chicago, Illinois, USA. This will use your `primary` token, unless you pass `--token` for something else. This server will automatically renew from your token's balance.

If you find the server off, check your token's balance with `sporestack token info`. If servers aren't able to automatically renew, they are powered off as a way to signal that payment is needed, else the server will be deleted. We don't have any way to email you if this is the case, given the nature of our service!

Make sure you match up your chosen provider with the flavor, operating system, and region options!

* `sporestack server stop --hostname SomeHostname`

Shutdown the server by hostname.

* `sporestack server stop --machine-id ss_m_...  # Or use --machine-id to be more pedantic.`

Shutdown the server by its machine ID, if it doesn't have a hostname, or if you want to be more pedantic.

* `sporestack server start --hostname SomeHostname`

Turn the server back on.

* `sporestack server autorenew-enable --hostname SomeHostname`

Enable autorenew on the server.

* `sporestack server autorenew-disable --hostname SomeHostname`

Disable autorenew on the server.

* `sporestack server list`

List your servers.

* `sporestack server info --hostname SomeHostname`

Get more detailed information on your server than the list view.

* `sporestack server delete --hostname SomeHostname`

Delete the server.

* `sporestack server launch --hostname SomeHostname --operating-system debian-12 --days 1 --provider digitalocean --flavor vps-1vcpu-1gb --region auto`

Launch a server on DigitalOcean, in a random region. This is for a one day fixed lifetime, after which it will be deleted if not renewed.

## Notes

* If you want to communicate with the SporeStack API using Tor, set this environment variable: `SPORESTACK_USE_TOR_ENDPOINT=1`. Verify which endpoint is in use with `sporestack api-endpoint`.

## Developing

* `pipenv install --deploy --dev`
* `pipenv run make test`
* `pipenv run make format` to format files and apply ruff fixes.

## Licence

[Unlicense/Public domain](LICENSE.txt)
