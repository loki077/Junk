#!/usr/bin/env python
# helloworld.py
__version__ = '0.1.0'

import re
import requests

URL = 'https://en.wikipedia.org/wiki/"Hello,_World!"_program'


def do_hello():
    result = requests.get(URL)
    print(re.findall('<title>(.*?)</title>', result.text)[0])


if __name__ == '__main__':
    do_hello()
