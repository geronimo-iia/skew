import unittest


class TestVersion(unittest.TestCase):
    def test_resource(self):
        from skew import __version__

        self.assertIsNotNone(__version__)
