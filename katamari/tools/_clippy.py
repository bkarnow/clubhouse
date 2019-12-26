#!/usr/bin/env python3
#
# Tool to build and install a Flatpak containing the Clippy Extension.
#
# Copyright (C) 2019 Endless Mobile, Inc.

from _common import (
    create_flatpak_manifest,
    build_flatpak,
    install_flatpak,
    build_bundle,
)

CONFIG_FILE = 'clippy.config.ini'

MANIFEST_FILE = 'katamari/com.hack_computer.Clippy.Extension.json'
APP_ID = 'com.hack_computer.Clippy.Extension'

MODULES = [
    'clippy',
]


def main(config, template=None):
    # Create the manifest:
    create_flatpak_manifest(config, MODULES, MANIFEST_FILE, template)
    if template:
        return

    repo = config.get('Advanced', 'repo')
    flatpak_branch = config.get_flatpak_branch()

    # Build the flatpak:
    build_flatpak(MANIFEST_FILE, config.get_flatpak_build_options())

    # Install the build in the system:
    if config.get('Common', 'install'):
        install_flatpak(repo, flatpak_branch, APP_ID, config.get_flatpak_install_options())

    # Build a flatpak bundle:
    if config.get('Common', 'bundle'):
        build_bundle(repo, flatpak_branch, APP_ID, options=['--runtime'])
