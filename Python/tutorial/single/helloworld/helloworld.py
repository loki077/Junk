#!/usr/bin/env python
# helloworld.py

import re
import requests

from helloworld.utils import show_message

URL = 'https://en.wikipedia.org/wiki/"Hello,_World!"_program'


def do_hello():
    result = requests.get(URL)
    show_message(re.findall('<title>(.*?)</title>', result.text)[0])


if __name__ == '__main__':
    do_hello() # pragma: no cover
