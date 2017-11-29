"""Test connectivity between to hosts in Mininet."""
import os
from unittest import TestCase

import pexpect

CONTAINER = 'kytos_tests'
IMAGE = 'kytos/systests'
PROMPT = 'root@.*:/usr/local/src/kytos# '
WITH_SUDO = True


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
        cls.execute(f'docker pull {IMAGE}', f'{IMAGE}:latest',
                    with_sudo=WITH_SUDO)

        # Verify whether the image is installed.
        cls.execute('docker images', f'{IMAGE}', with_sudo=WITH_SUDO)

        # Start the container to run the tests
        cmd = f'docker run --rm -it --name {CONTAINER} {IMAGE}'
        cls._kytos = cls.execute(cmd, PROMPT, with_sudo=WITH_SUDO)

    def test000_uname_a(self):
        """Test expected 'uname -a' command using the container."""
        expected = ["Linux", "4.13.0-1-amd64", "#1 SMP Debian 4.13.4-2"]
        self._kytos.sendline('uname -a')
        self._kytos.expect(expected)
        self._kytos.expect(PROMPT)

    def test00_update_repositories(self):
        """Update all repositories."""
        self._kytos.sendline('kytos-update')
        self._kytos.expect(['Fast-forward', 'up-to-date'])
        self._kytos.expect(PROMPT)

    def test01_install_projects(self):
        """Install Kytos projects from cloned repository in safe order."""
        pip = 'pip install --no-index --find-links $KYTOSDEPSDIR .'
        PROJECTS = ['python-openflow']
        for project in PROJECTS:
            self._kytos.sendline(f'cd $KYTOSDIR/{project}; {pip}; cd -')
            self._kytos.expect(f'Successfully installed .*{project}', timeout=30)
            self._kytos.expect(PROMPT)

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
