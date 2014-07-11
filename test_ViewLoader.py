__author__ = 'hoseinyeganloo@gmail.com'

import unittest
import ViewLoader
import pyrazor


class MyTestCase(unittest.TestCase):


    def test_Render(self):
        ref = open('sampleView/helloWorld.html')
        self.assertEqual(ref.read(),pyrazor.Render(ViewLoader.ViewLoader.View('sampleView/helloWorld.pyhtml'),'Hello World',False))

    def test_Render(self):
        ref = open('sampleView/child.html')
        self.assertEqual(ref.read(),pyrazor.Render(ViewLoader.ViewLoader.View('sampleView/Layout.pyhtml'),'Hello World',False))
        #print(pyrazor.Render(ViewLoader.ViewLoader.View('sampleView/Layout.pyhtml'),'Hello World',False))


if __name__ == '__main__':
    unittest.main()
