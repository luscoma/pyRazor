__author__ = 'hoseinyeganloo@gmail.com'

import unittest
from ViewLoader import ViewLoader
import pyrazor


class MyTestCase(unittest.TestCase):

    # Test loading Pages
    def test_Render(self):
        ref = open('sampleView/helloWorld.html')
        self.assertEqual(ref.read(),pyrazor.Render(ViewLoader.Load('sampleView/helloWorld.pyhtml'),'Hello World',False))

    # Test Layout & body
    def test_Render(self):
        ref = open('sampleView/child.html')
        #self.assertEqual(ref.read(),pyrazor.Render(ViewLoader.Load('sampleView/child.pyhtml'),'Hello World',False))
        print(pyrazor.Render(ViewLoader.Load('sampleView/child.pyhtml'),"Hello World"))


if __name__ == '__main__':
    unittest.main()
