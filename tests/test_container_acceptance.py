"""Regressions for real Docker metadata observed during Linux acceptance."""

import ipaddress
import unittest

from tools.container_acceptance import unused_subnet


class TestDockerNetworkMetadata(unittest.TestCase):
    def test_null_builtin_network_config_and_existing_subnets(self):
        networks = [
            {"Name": "host", "IPAM": {"Config": None}},
            {"Name": "none", "IPAM": None},
            {"Name": "existing", "IPAM": {"Config": [{"Subnet": "172.28.0.0/24"}]}},
            {"Name": "ipv6", "IPAM": {"Config": [{"Subnet": "fd00::/64"}]}},
        ]
        self.assertEqual(unused_subnet(networks), ipaddress.ip_network("172.28.1.0/24"))
