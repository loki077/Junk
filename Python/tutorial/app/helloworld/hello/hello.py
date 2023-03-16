#!/usr/bin/env python

import re
import requests

from helloworld.hello.utils import show_message
from helloworld.world.world import translate_hello


URL = 'https://en.wikipedia.org/wiki/"Hello,_World!"_program'


def do_hello():
    """Main entry point for the program, does the look-up and translation"""
    result = requests.get(URL)

    message = re.findall('<title>(.*?)</title>', result.text)[0]
    show_message(f'en:{message}')

    for lang, greeting in translate_hello().items():
        translation = message.replace('Hello', greeting)
        show_message(f'{lang}:{translation}')
