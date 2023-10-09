import copy
import os.path
import unittest

from loguru import logger

from bilibili_api.wbi import get_wbi, WBI_CACHE_FILE, WBI_TS_KEY
from local_storage import LocalStorage


def clean():
    if os.path.exists('.wbi_cache'):
        os.remove('.wbi_cache')


class TestWbi(unittest.TestCase):
    def test_get_wbi(self):
        val = get_wbi()
        self.assertTrue(val is not None)
        clean()

    def test_get_wbi_twice(self):
        val = get_wbi()
        self.assertTrue(val is not None)
        val = get_wbi()
        self.assertTrue(val is not None)
        clean()

    def test_get_failed(self):
        from bilibili_api.urls import UrlData
        tmp = UrlData.URL_NAV
        UrlData.URL_NAV = 'https://127.0.0.1:12345'
        val = get_wbi()
        self.assertIs(val, None)
        clean()
        UrlData.URL_NAV = tmp

    def test_ts_invalid(self):
        wbi_cache = LocalStorage(WBI_CACHE_FILE)
        tmp = copy.copy(wbi_cache)
        wbi_cache.put(WBI_TS_KEY, '1#2')
        wbi_cache.save()
        _ = get_wbi()
        self.assertLogs(logger, "WARNING")
        wbi_cache.put(WBI_TS_KEY, '1#2#3#4#5')
        wbi_cache.save()
        _ = get_wbi()
        self.assertLogs(logger, "WARNING")
        tmp.save()

