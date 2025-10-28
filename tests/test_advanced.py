# -*- coding: utf-8 -*-

from .context import moonshinewrangler

import unittest


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_thoughts(self):
        self.assertIsNone(moonshinewrangler.hmm())


if __name__ == '__main__':
    unittest.main()
