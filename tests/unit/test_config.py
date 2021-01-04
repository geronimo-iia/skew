import os
import unittest

import mock

from skew.config import get_accounts, get_config, get_credentials, get_profile


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.environ = {}
        self.environ_patch = mock.patch('os.environ', self.environ)
        self.environ_patch.start()
        credential_path = os.path.join(os.path.dirname(__file__), 'cfg', 'aws_credentials')
        self.environ['AWS_CONFIG_FILE'] = credential_path
        config_path = os.path.join(os.path.dirname(__file__), 'cfg', 'skew.yml')
        self.environ['SKEW_CONFIG'] = config_path

    def test_get_config(self):
        self.assertIsNotNone(get_config())

    def test_get_accounts(self):
        self.assertIsNotNone(get_config())
        self.assertEqual(4, len(get_accounts().keys()))
        self.assertIn("123456789012", get_accounts().keys())

    def test_get_profile(self):
        self.assertEqual("foo", get_profile(account_id="123456789012"))

    def test_get_credentials(self):
        self.assertIsNone(get_credentials("123456789012"))
