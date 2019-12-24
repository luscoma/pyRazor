__author__ = 'hoseinyeganloo@gmail.com'

import unittest
from razorview import pyRazor
import logging


class MyTestCase(unittest.TestCase):

    # Test Layout & body
    def test_Render(self):
        print(pyRazor.RenderFile('sampleView/child.pyhtml'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    unittest.main()
