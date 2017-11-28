"""Test connectivity between to hosts in Mininet."""
import os
from unittest import TestCase

import pexpect

CONTAINER = 'kytos_tests'
IMAGE = 'kytos/systests'
PROMPT = 'root@.*:/usr/local/src/kytos# '
WITH_SUDO =  False if os.geteuid() else True


class TestStruct(TestCase):
    """Test the alpine container."""

    @classmethod
    def execute(cls, command, expected=None, timeout=60, with_sudo=False):
        """Execute command inside the bash"""
        if with_sudo:
            command = 'sudo ' + command
        terminal = pexpect.spawn(command)
        if expected is not None:
            terminal.expect(expected, timeout=timeout)
        return terminal

    @classmethod
    def setUpClass(cls):
        """Setup the container.

        Download the image and starts a new container.
        """
        cls.execute('dockerd', with_sudo=True)
        cls.execute('service docker start', with_sudo=True)

        # Download the container
        cls.execute(f'docker pull {IMAGE}', f'{IMAGE}:latest', with_sudo=WITH_SUDO)

        # Verify whether the image is installed.
        cls.execute('docker images', f'{IMAGE}')

        # Start the container to run the tests
        cmd = f'docker run --rm -it --name {CONTAINER} {IMAGE}'
        cls._kytos = cls.execute(cmd, PROMPT, with_sudo=WITH_SUDO)

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
