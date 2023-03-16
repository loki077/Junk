#!/usr/bin/env python 
# tests.py -- for helloworld

from unittest import TestCase
from unittest.mock import patch

from helloworld import do_hello, URL

class FakeResult:
    text = '<title>"Hello, World!" program - Wikipedia</title>'

class TestHelloWorld(TestCase):

    @patch('requests.get')
    def test_helloworld(self, mock_get):
        mock_get.return_value = FakeResult()

        do_hello()
        mock_get.assert_called_with(URL)

if __name__ == '__main__':
    from unittest import main
    main()
