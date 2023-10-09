import json
import time
import urllib
from datetime import datetime
from functools import reduce
from typing import Optional

from Crypto.Hash import MD5
from loguru import logger

from local_storage import LocalStorage
from . import session
from .urls import UrlData

WBI_CACHE_FILE = r'.wbi_cache'
WBI_IMG_KEY = 'wbi_img'
WBI_SUB_KEY = 'wbi_sub'
WBI_TS_KEY = 'wbi_ts'
MIXIN_ENC_TABLE = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]


def _datetiem_to_str(dt: datetime) -> str:
    d = dt.day
    m = dt.month
    y = dt.year
    return f"{y}#{m}#{d}"


def _time_check(dt: str) -> bool:
    dt = dt.split('#')
    if len(dt) != 3:
        logger.warning("Wbi timestamp is invalid! Refresh required!")
        return False
    y, m, d = map(lambda x: int(x), dt)
    today = datetime.now()
    ty, tm, td = today.year, today.month, today.day
    return y == ty and m == tm and d == td


def process_key(img: str, sub: str) -> tuple[str, str]:
    def proc_fun(a: str) -> str:
        a = a.rsplit('/', 1)[1]
        a = a.split('.', 1)[0]
        return a

    return proc_fun(img), proc_fun(sub)


def get_wbi() -> Optional[tuple[str, str]]:
    wbi_cache = LocalStorage(WBI_CACHE_FILE)
    ts = wbi_cache.get(WBI_TS_KEY, None)
    if ts is not None:
        if _time_check(ts):
            img, sub = wbi_cache.get(WBI_IMG_KEY), wbi_cache.get(WBI_SUB_KEY)
            if img is not None and sub is not None:
                return img, sub
    try:
        reply = session.get(UrlData.URL_NAV)
        obj = json.loads(reply.text)
        wbi = obj['data']['wbi_img']
        img, sub = wbi['img_url'], wbi['sub_url']
        img, sub = process_key(img, sub)
        wbi_cache.put(WBI_IMG_KEY, img)
        wbi_cache.put(WBI_SUB_KEY, sub)
        wbi_cache.put(WBI_TS_KEY, _datetiem_to_str(datetime.now()))
        wbi_cache.save()
        return img, sub
    except (IOError, KeyError, ValueError):
        return None


def get_mixin_key(img_key: str, sub_key: str) -> str:
    cat = img_key + sub_key
    return reduce(lambda s, i: s + cat[i], MIXIN_ENC_TABLE, '')[:32]


def enc_wbi(params: dict, img_key: str, sub_key: str) -> dict:
    mixin_key = get_mixin_key(img_key, sub_key)
    cur_time = round(time.time())
    params['wts'] = cur_time
    params = dict(sorted(params.items()))
    params = {
        k: ''.join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v
        in params.items()
    }
    query = urllib.parse.urlencode(params)  # 序列化参数
    wbi_sign = MD5.new((query + mixin_key).encode('utf8')).hexdigest().lower()
    params['w_rid'] = wbi_sign
    return params
