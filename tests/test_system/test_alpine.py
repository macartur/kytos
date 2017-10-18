"""Test connectivity between to hosts in Mininet."""
from unittest import TestCase

import pexpect

CONTAINER = 'kytos_tests'
IMAGE = 'alpine'
PROMPT = '/ # '


class TestAlpine(TestCase):
    """Test the alpine container."""

    @classmethod
    def setUpClass(cls):
        """Setup the alpine container.

        Download the alpine image and starts a new container.
        """
        # Start the docker daemon
#        cls._kytos = pexpect.spawn(f'sudo dockerd')
        cls._kytos = pexpect.spawn(f'sudo service docker start')
        cls._kytos.expect(pexpect.EOF)

        # Download the alpine container
        cls._kytos = pexpect.spawn(f'sudo docker pull alpine')
        expected = ['Status: Downloaded newer image for alpine:latest']
        cls._kytos.expect(expected, timeout=120)

        # Verify whether the alpine image is installed.
        cls._kytos = pexpect.spawn(f'sudo docker images')
        cls._kytos.expect('alpine', timeout=60)

        # Start the alpine container to run the tests
        cls._kytos = pexpect.spawn(
            f'sudo docker run --rm -it --privileged --name {CONTAINER} {IMAGE}'
        )
        cls._kytos.expect(PROMPT, timeout=60)

    def test0000_uname_a(self):
        """Test expected 'uname -a' command using the container."""
        expected = ["Linux", "4.13.0-1-amd64", "#1 SMP Debian 4.13.4-2"]
        self._kytos.sendline('uname -a')
        self._kytos.expect(expected)

    @classmethod
    def tearDownClass(cls):
        """Stop container."""
        bash = pexpect.spawn('/bin/bash')
        bash.sendline(f'sudo docker kill {CONTAINER} && exit')
        bash.expect(f'\r\n{CONTAINER}\r\n', timeout=120)
        bash.wait()
