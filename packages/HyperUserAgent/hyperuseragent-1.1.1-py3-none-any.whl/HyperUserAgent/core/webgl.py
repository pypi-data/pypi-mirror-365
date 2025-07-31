import random, hashlib, struct


class WebGLFingerprint:
    """
    Simulate WebGL shader hash per device.
    """

    @staticmethod
    def simulate(rng: random.Random) -> str:
        vendor = rng.choice(["Intel", "AMD", "NVIDIA", "Apple"])
        renderer = (
            f"{vendor} {rng.choice(['RTX','RX','UHD','M1'])}"
            f" {rng.randint(1000,9000)}"
        )
        ver = f"{rng.randint(3,4)}.{rng.randint(0,6)}"
        raw = f"{vendor}|{renderer}|{ver}"
        return hashlib.sha256(raw.encode()).hexdigest()
