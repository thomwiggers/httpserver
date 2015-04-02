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

    def setUp(self):
        """Set up selenium"""
        super(TestSelenium, self).setUp()
        driver = os.environ.get("SELENIUM_WEBDRIVER", "Firefox")
        if driver == "phantomjs":
            self.driver = webdriver.PhantomJS()
        elif driver == "chrome":
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(3)

        self.process = multiprocessing.Process(
            target=_start_server,
            args=(_ip, _port, _host, _dir))
        self.process.start()

    def test_get_index(self):
        hostname = 'http://{}:{}'.format(_host, _port)
        self.driver.get(hostname)
        self.driver.find_elements_by_tag_name('title')
        self._sleep()
        assert '<title>Index</title>' in self.driver.page_source

    def test_get_404(self):
        path = 'http://{}:{}/notfound'.format(_host, _port)
        self.driver.get(path)
        self._sleep()
        assert 'Not Found' in self.driver.page_source

    def tearDown(self):
        super(TestSelenium, self).tearDown()
        self.process.terminate()
        self.driver.quit()

if __name__ == '__main__':
    unittest.main()
