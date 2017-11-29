"""Test connectivity between to hosts in Mininet."""
import os
from unittest import TestCase

import pexpect

CONTAINER = 'kytos_tests'
IMAGE = 'kytos/systests'
PROMPT = 'root@.*:/usr/local/src/kytos# '
WITH_SUDO = True if (os.environ.get('USER') is None) else False
PROJECTS = ['python-openflow', 'kytos-utils', 'kytos']
NAPPS = ['kytos/of_core', 'kytos/of_lldp']

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

        cls.execute('service docker start', 'docker start/running', with_sudo=True)

        # Download the container
        cls.execute(f'docker pull {IMAGE}', f'{IMAGE}:latest',
                    with_sudo=WITH_SUDO)

        # Verify whether the image is installed.
        cls.execute('docker images', f'{IMAGE}', with_sudo=WITH_SUDO)

        # Start the container to run the tests
        cmd = f'docker run --rm -it --name {CONTAINER} {IMAGE}'
        cls._kytos = cls.execute(cmd, PROMPT, with_sudo=WITH_SUDO)

#        cmd = f'docker exec -it --privileged {CONTAINER} /bin/bash'
#        cls._mininet = cls.execute(cmd, PROMPT, with_sudo=WITH_SUDO)

        cls._kytos.sendline("pip install ruamel.yaml")
        cls._kytos.expect("Successfully installed ruamel.yaml")

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

        for project in PROJECTS:
            self._kytos.sendline(f'cd $KYTOSDIR/{project}; {pip}; cd -')
            self._kytos.expect(f'Successfully installed .*{project}',
                               timeout=60)
            self._kytos.expect(PROMPT)

    def test02_launch_kytosd(self):
        """kytos-utils requires kytosd to be running."""
        self._kytos.sendline('kytosd -f')
        # Regex is for color codes
        self._kytos.expect(r'kytos \$> ')

#    def test03_install_napps(self):
#        """Install NApps for the ping to work.
#
#
#        As self._kytos is blocked in kytosd shell, we use mininet terminal.
#        """
#        for napp in NAPPS:
#            self._mininet.sendline(f'kytos napps install {napp}')
#            self._mininet.expect('INFO      Enabled.')
#            napp_name = napp.split('/')[0]
#            self._kytos.expect(napp_name +'.+Running NApp')
#            self._mininet.expect(PROMPT)

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
