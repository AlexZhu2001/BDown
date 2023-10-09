import json
from datetime import datetime
from typing import Optional

from loguru import logger

from local_storage import LocalStorage
from . import session
from .urls import UrlData

WBI_CACHE_FILE = r'.wbi_cache'
WBI_IMG_KEY = 'wbi_img'
WBI_SUB_KEY = 'wbi_sub'
WBI_TS_KEY = 'wbi_ts'


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
        img = wbi['img_url']
        sub = wbi['sub_url']
        wbi_cache.put(WBI_IMG_KEY, img)
        wbi_cache.put(WBI_SUB_KEY, sub)
        wbi_cache.put(WBI_TS_KEY, _datetiem_to_str(datetime.now()))
        wbi_cache.save()
        return img, sub
    except (IOError, KeyError, ValueError):
        return None
