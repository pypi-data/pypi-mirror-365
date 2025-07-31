"""
Full-stack browser-fingerprint simulator:
Canvas, WebGL, Audio, TLS, HTTP/2, screen, plugins, languages, memory, timing.
"""

from __future__ import annotations
import random, base64, hashlib, os, time
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple
from .tls import TLSFingerprint
from .http2 import H2Fingerprint
from .canvas import CanvasFingerprint
from .webgl import WebGLFingerprint


@dataclass
class Fingerprint:
    ua_string: str
    screen: Dict[str, int]
    languages: List[str]
    platform: str
    plugins: List[str]
    memory: int
    timezone: str
    canvas_fp: str
    webgl_fp: str
    tls_fp: str
    h2_fp: str

    # ---------------- creation helpers ----------------
    @classmethod
    def generate(cls, ua: str, seed: int | None = None) -> "Fingerprint":
        rng = random.Random(seed)
        screen = rng.choice(
            [
                {"w": 1920, "h": 1080, "d": 24},
                {"w": 2560, "h": 1440, "d": 24},
                {"w": 1366, "h": 768, "d": 24},
                {"w": 375, "h": 812, "d": 32},
            ]
        )
        platform = ("Win64", "MacIntel", "Linux x86_64", "Android")[rng.randint(0, 3)]
        plugins = ["PDF Viewer", "Chrome PDF", "NaCl", "Widevine"]
        languages = ["en-US", "en"]
        memory = rng.choice([4, 8, 16])
        tzmin = rng.randint(-720, 720)
        timezone = f"{tzmin//60:+03d}:{abs(tzmin)%60:02d}"

        canvas_fp = CanvasFingerprint.simulate(rng)
        webgl_fp = WebGLFingerprint.simulate(rng)
        tls_fp = TLSFingerprint.simulate(rng)
        h2_fp = H2Fingerprint.simulate(rng)
        return cls(
            ua,
            screen,
            languages,
            platform,
            plugins,
            memory,
            timezone,
            canvas_fp,
            webgl_fp,
            tls_fp,
            h2_fp,
        )

    # ---------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
