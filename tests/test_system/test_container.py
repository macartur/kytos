"""Test container module."""
from .struct import TestStruct


class TestContainer(TestStruct):
    """Container class."""

    def test_uname_a(self):
        """Test expected 'uname -a' command using the container."""
        expected = ["Linux", "4.13.0-1-amd64", "#1 SMP Debian 4.13.4-2"]
        self._kytos.sendline('uname -a')
        self._kytos.expect(expected)
