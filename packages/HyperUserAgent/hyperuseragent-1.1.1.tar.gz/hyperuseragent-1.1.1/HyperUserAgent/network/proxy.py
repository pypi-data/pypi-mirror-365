import random, itertools, pathlib, json
from typing import Iterator, Tuple, Optional


class ProxyPool:
    """Rotating proxy manager supporting HTTP/SOCKS & sticky sessions."""

    def __init__(
        self, src: str | pathlib.Path, sticky: int = 10, seed: Optional[int] = None
    ):
        self.proxies = json.load(open(src))
        self.rng = random.Random(seed)
        self.sticky = sticky
        self._counter = itertools.count()

    def next(self) -> Tuple[str, int]:
        if next(self._counter) % self.sticky == 0:
            self._current = self.rng.choice(self.proxies)
        return self._current["host"], self._current["port"]
