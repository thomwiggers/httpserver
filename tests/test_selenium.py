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
import time

from httpserver import _start_server

from selenium import webdriver

_host = 'localhost'
_ip = '127.0.0.1'
_port = 1234
_dir = os.path.join(os.path.dirname(__file__), 'fixtures/selenium')


class TestSelenium(unittest.TestCase):

    def _sleep(self):
        if not isinstance(self.driver, webdriver.PhantomJS):
            time.sleep(3)

    @classmethod
    def setUpClass(cls):
        """Set up selenium"""
        driver = os.environ.get("SELENIUM_WEBDRIVER", "Firefox")
        if driver == "phantomjs":
            cls.driver = webdriver.PhantomJS()
        elif driver == "chrome":
            cls.driver = webdriver.Chrome()
        else:
            cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(3)
        super(TestSelenium, cls).setUpClass()

    def setUp(self):
        self.process = multiprocessing.Process(
            target=_start_server,
            args=(_ip, _port, _host, _dir))
        self.process.start()

    def test_get_index(self):
        hostname = 'http://{}:{}'.format(_host, _port)
        self.driver.get(hostname)
        self._sleep()
        assert '<title>Index</title>' in self.driver.page_source

    def test_get_404(self):
        path = 'http://{}:{}/notfound'.format(_host, _port)
        self.driver.get(path)
        self._sleep()
        assert 'Not Found' in self.driver.page_source

    def tearDown(self):
        self.process.terminate()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(TestSelenium, cls).tearDownClass()

if __name__ == '__main__':
    unittest.main()
