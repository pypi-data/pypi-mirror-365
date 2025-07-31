import httpx, time, types, random, ssl
from ..core.ua import UA
from ..core.fingerprint import Fingerprint
from .proxy import ProxyPool
from typing import Optional


class HyperSession(httpx.Client):
    """
    Drop-in replacement for requests.Session with:
      • Dynamic UA + headers
      • TLS & HTTP/2 fingerprints
      • Rotating proxies
      • Behavioural throttling (human-like delays)
    """

    def __init__(
        self,
        proxy_pool: Optional[ProxyPool] = None,
        platform="desktop",
        browser=None,
        timeout=30.0,
        **kw,
    ):
        self.ua_gen = UA()
        headers = kw.pop("headers", {})
        self.pool = proxy_pool
        super().__init__(http2=True, timeout=timeout, headers=headers, **kw)
        self._platform = platform
        self._browser = browser

    # override main request --------------------------------------------------
    def request(self, method, url, **kwargs):
        # rotate UA each navigation
        ua = self.ua_gen.random(self._platform, self._browser)
        fp = Fingerprint.generate(ua)
        hdr = {
            "User-Agent": ua,
            "Accept-Language": ",".join(fp.languages),
            "Sec-Ch-Ua-Platform": f'"{fp.platform}"',
            "Sec-Fetch-Site": "none",
            "X-Canvas-FP": fp.canvas_fp[:16],  # custom header for demo
        }
        kwargs.setdefault("headers", {}).update(hdr)

        # proxy
        if self.pool:
            host, port = self.pool.next()
            kwargs["proxies"] = f"http://{host}:{port}"

        # behaviour-throttling
        time.sleep(random.uniform(0.4, 1.3))
        return super().request(method, url, **kwargs)
