#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_selenium
----------------------------------

Tests the http server with a real browser.
"""
import os
import unittest
import multiprocessing

from httpserver.httpserver import HttpProtocol
from httpserver import _start_server

from selenium import webdriver

_host = 'localhost'
_ip = '127.0.0.1'
_port = 1234
_dir = os.path.join(os.path.dirname(__file__), 'fixtures')

class TestSelenium(unittest.TestCase):
    
    def setUpClass(self):
        self.process = multiprocessing.Process(target=_start_server,
                                               args=(
                                                 _ip,
                                                 _port,
                                                 _host,
                                                 _dir))
        self.process.start()

    def setUp(self):
        self.driver = webdriver.Firefox()

    def get_index(self):
        self.driver.get('http://localhost/')

    def tearDown(self):
        self.driver.close()

    def tearDownClass(self):
        self.process.terminate()

if __name__ == '__main__':
    unittest.main()
