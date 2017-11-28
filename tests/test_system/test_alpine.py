"""Test connectivity between to hosts in Mininet."""
import os
import sys
from unittest import TestCase

import pexpect

CONTAINER = 'kytos_tests'
IMAGE = 'alpine'
PROMPT = '/ # '
WITH_SUDO = False if os.geteuid() != 0 else True


class TestAlpine(TestCase):
    """Test the alpine container."""

    @classmethod
    def execute(cls, command, expected=None, timeout=60, with_sudo=False):
        """Execute command inside the bash"""
        if with_sudo:
            command = 'sudo ' + command
        cls._kytos = pexpect.spawn(command)
        if expected is not None:
            cls._kytos.expect(expected, timeout=timeout)

    @classmethod
    def setUpClass(cls):
        """Setup the alpine container.

        Download the alpine image and starts a new container.
        """
        cls.execute('dockerd', with_sudo=True)
        cls.execute('service docker start', with_sudo=True)

        # Download the alpine container
        cls.execute('docker pull alpine', 'alpine:latest', with_sudo=WITH_SUDO)

        # Verify whether the alpine image is installed.
        cls.execute('docker images', 'alpine')

        # Start the alpine container to run the tests
        cmd = f'docker run --rm -it --name {CONTAINER} {IMAGE}'
        cls.execute(cmd, PROMPT, with_sudo=WITH_SUDO)

    def test0000_uname_a(self):
        """Test expected 'uname -a' command using the container."""
        expected = ["Linux", "4.13.0-1-amd64", "#1 SMP Debian 4.13.4-2"]
        self._kytos.sendline('uname -a')
        self._kytos.expect(expected)

    @classmethod
    def tearDownClass(cls):
        """Stop container."""
        bash = pexpect.spawn('/bin/bash')
        command = f'docker kill {CONTAINER} && exit'
        if WITH_SUDO:
            command = 'sudo ' + command
        bash.sendline(command)
        bash.expect(f'\r\n{CONTAINER}\r\n', timeout=120)
        bash.wait()
