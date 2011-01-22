import unittest

class APIVersionTestCase (unittest.TestCase):

    def test_compare_versions(self):
        self.assert_('2010-01-01' > '2009-01-01' > '2008-01-01')
        self.assert_('2010-01-01' >= '2010-01-01' < '2010-01-02')
