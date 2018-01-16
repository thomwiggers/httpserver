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
_port = 5837
_dir = os.path.join(os.path.dirname(__file__), 'fixtures/selenium')
WAIT_TIME = 4


def _which(program):
    """Find a file on the PATH

    https://stackoverflow.com/a/377028/248065
    """
    def _is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if _is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if _is_exe(exe_file):
                return exe_file

    raise ValueError("Program not found")


class TestSelenium(unittest.TestCase):

    def _sleep(self):
        time.sleep(WAIT_TIME)

    def setUp(self):
        """Set up selenium"""
        super(TestSelenium, self).setUp()
        driver = os.environ.get("SELENIUM_WEBDRIVER", "Firefox")
        if driver == "phantomjs":
            self.driver = webdriver.PhantomJS()
        elif driver == "chrome":
            options = webdriver.chrome.options.Options()
            options.set_headless()
            if os.environ.get('CI'):  # Travis bug
                options.add_argument('--no-sandbox')
            options.binary_location = _which('google-chrome-stable')
            self.driver = webdriver.Chrome(chrome_options=options)
        else:
            options = webdriver.firefox.options.Options()
            options.set_headless()
            options.binary = _which('firefox')
            self.driver = webdriver.Firefox(firefox_options=options)
        self.driver.implicitly_wait(WAIT_TIME)

        self.process = multiprocessing.Process(
            target=_start_server,
            args=(_ip, _port, _host, _dir))
        self.process.start()
        time.sleep(4)

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
