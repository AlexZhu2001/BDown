import inspect
import os.path
import time
import unittest

from loguru import logger

from bilibili_api.wbi import get_wbi, WBI_CACHE_FILE, WBI_TS_KEY, process_key, get_mixin_key, enc_wbi
from local_storage import LocalStorage


def clean():
    if os.path.exists('.wbi_cache'):
        os.remove('.wbi_cache')


class TestWbi(unittest.TestCase):
    pk_original = ("https://i0.hdslb.com/bfs/wbi/653657f524a547ac981ded72ea172057.png",
                   "https://i0.hdslb.com/bfs/wbi/6e4909c702f846728e64f6007736a338.png")
    pk_corr = ("653657f524a547ac981ded72ea172057", "6e4909c702f846728e64f6007736a338")
    pk_mixin = "72136226c6a73669787ee4fd02a74c27"
    params = {
        'bar': '514',
        'foo': '114',
        'zab': '1919810'
    }
    after_wbi = {
        'bar': '514',
        'foo': '114',
        'wts': '1684746387',
        'zab': '1919810',
        'w_rid': '90efcab09403023875b8516f07e9f9de'
    }
    ts_less = '1#2'
    ts_more = '1#2#3#4#5'
    NOT_ALLOWED_URL = 'https://example.com/404.html'

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
        _ = get_wbi()
        wbi_cache = LocalStorage(WBI_CACHE_FILE)
        wbi_cache.put(WBI_TS_KEY, self.ts_less)
        wbi_cache.save()
        _ = get_wbi()
        self.assertLogs(logger, "WARNING")
        wbi_cache.put(WBI_TS_KEY, self.ts_more)
        wbi_cache.save()
        _ = get_wbi()
        self.assertLogs(logger, "WARNING")
        clean()

    def test_process_key(self):
        ans = process_key(*self.pk_original)
        self.assertEqual(self.pk_corr, ans)

    def test_get_mixin_key(self):
        ans = process_key(*self.pk_original)
        mixin = get_mixin_key(*ans)
        self.assertEqual(mixin, self.pk_mixin)

    def test_enc_wbi(self):
        bak = time.time
        inspect.currentframe()
        time.time = lambda: 1684746387
        ans = enc_wbi(self.params, *self.pk_corr)
        self.assertDictEqual(ans, self.after_wbi)
        time.time = bak
