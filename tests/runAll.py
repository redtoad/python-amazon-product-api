#!/usr/bin/python
# Usage: ./runAll.py --with-xunit --with-coverage
import os, sys
# change to tests directory and make sure that the current source (in parent
# directory) is always imported first
os.chdir(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, '..')

import nose
from tests import XMLResponseTestLoader
nose.main(testLoader=XMLResponseTestLoader)
