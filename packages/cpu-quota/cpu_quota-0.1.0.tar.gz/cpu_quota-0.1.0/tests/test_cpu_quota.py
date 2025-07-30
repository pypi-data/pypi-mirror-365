import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
from io import StringIO

from cpu_quota.core import (
    get_cpu_quota_from_systemd, 
    get_available_cpus, 
    get_available_cpus_conservative,
    get_parallel_workers,
    get_conservative_parallel_workers
)


class TestCPUQuota(unittest.TestCase):
    
    @patch('cpu_quota.core.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="[Service]\nCPUQuota=400%\n")
    @patch('cpu_quota.core.os.getuid', return_value=1000)
    def test_get_cpu_quota_percentage(self, mock_getuid, mock_file, mock_exists):
        mock_exists.return_value = True
        quota = get_cpu_quota_from_systemd()
        self.assertEqual(quota, 4.0)
    
    @patch('cpu_quota.core.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="[Service]\nCPUQuota=2.5\n")
    @patch('cpu_quota.core.os.getuid', return_value=1000)
    def test_get_cpu_quota_decimal(self, mock_getuid, mock_file, mock_exists):
        mock_exists.return_value = True
        quota = get_cpu_quota_from_systemd()
        self.assertEqual(quota, 2.5)
    
    @patch('cpu_quota.core.Path.exists')
    def test_get_cpu_quota_no_file(self, mock_exists):
        mock_exists.return_value = False
        quota = get_cpu_quota_from_systemd()
        self.assertIsNone(quota)
    
    @patch('cpu_quota.core.get_cpu_quota_from_systemd', return_value=3.7)
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_available_cpus_with_quota(self, mock_stdout, mock_quota):
        result = get_available_cpus()
        self.assertEqual(result, 3)  # floor(3.7)
        output = mock_stdout.getvalue()
        self.assertIn("Systemd CPU quota: 3.70", output)
        self.assertIn("Available CPUs (floor): 3", output)
    
    @patch('cpu_quota.core.get_cpu_quota_from_systemd', return_value=None)
    @patch('cpu_quota.core.os.cpu_count', return_value=4)
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_available_cpus_without_quota(self, mock_stdout, mock_cpu_count, mock_quota):
        result = get_available_cpus()
        self.assertEqual(result, 4)
        output = mock_stdout.getvalue()
        self.assertIn("No systemd CPU quota found", output)
    
    @patch('cpu_quota.core.get_available_cpus', return_value=6)
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_available_cpus_conservative_large(self, mock_stdout, mock_get_cpus):
        # For > 4 CPUs, should reserve 1 CPU
        result = get_available_cpus_conservative()
        self.assertEqual(result, 5)  # 6 - 1
    
    @patch('cpu_quota.core.get_available_cpus', return_value=3)
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_available_cpus_conservative_medium(self, mock_stdout, mock_get_cpus):
        # For 2 < CPUs <= 4, should use 75%
        result = get_available_cpus_conservative()
        self.assertEqual(result, 2)  # max(1, int(3 * 0.75))
    
    @patch('cpu_quota.core.get_available_cpus', return_value=2)
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_available_cpus_conservative_small(self, mock_stdout, mock_get_cpus):
        # For <= 2 CPUs, should use all
        result = get_available_cpus_conservative()
        self.assertEqual(result, 2)
    
    @patch('cpu_quota.core.get_available_cpus', return_value=4)
    def test_get_parallel_workers(self, mock_get_cpus):
        result = get_parallel_workers()
        self.assertEqual(result, 4)
    
    @patch('cpu_quota.core.get_available_cpus_conservative', return_value=3)
    def test_get_conservative_parallel_workers(self, mock_get_conservative):
        result = get_conservative_parallel_workers()
        self.assertEqual(result, 3)


if __name__ == '__main__':
    unittest.main()