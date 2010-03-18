import unittest

# Preprend parent directory to PYTHONPATH to ensure that this amazonproduct
# module can be imported and will take precedence over an existing one
import os.path, sys
_here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_here, '..'))

from amazonproduct import API
from amazonproduct import UnknownLocale

class LocalesTestCase (unittest.TestCase):

    """
    Testing initialising API with different locales.
    """

    ACCESS_KEY = SECRET_KEY = ''

    def test_fails_for_invalid_locale(self):
        self.assertRaises(UnknownLocale, API, self.ACCESS_KEY,
                self.SECRET_KEY, locale='XX')

if __name__ == '__main__':
    unittest.main()
