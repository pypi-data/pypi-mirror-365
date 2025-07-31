import random, hashlib


class H2Fingerprint:
    """
    Generate Akamai-style HTTP/2 settings-frame fingerprint.
    """

    _settings = [1, 2, 3, 4, 6]  # SETTINGS_ identifiers

    @staticmethod
    def simulate(rng: random.Random) -> str:
        pairs = [
            f"{sid}:{rng.randint(16, 65535)}"
            for sid in rng.sample(H2Fingerprint._settings, rng.randint(3, 5))
        ]
        order = "".join(rng.sample("masp", 4))  # pseudo-header order
        frame = ",".join(map(str, rng.sample(range(0, 256, 32), 4)))
        raw = "[" + ";".join(pairs) + "]|" + order + "|" + frame
        return hashlib.sha1(raw.encode()).hexdigest()
