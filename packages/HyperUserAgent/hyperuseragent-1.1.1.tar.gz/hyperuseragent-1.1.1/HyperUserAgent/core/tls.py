import random, hashlib


class TLSFingerprint:
    """
    Generates JA3-like TLS ClientHello signatures with randomised ciphers &
    extensions matching the selected browser family.
    """

    _ciphers = [
        4867,
        4865,
        49195,
        49199,
        52393,
        52392,
        49196,
        49200,
        49171,
        49172,
        157,
        53,
        47,
        255,
    ]

    _ext = [0, 10, 11, 13, 16, 18, 23, 27, 28, 35, 43, 45, 51]

    @staticmethod
    def simulate(rng: random.Random) -> str:
        ver = rng.choice([771, 772])
        sel = rng.sample(
            TLSFingerprint._ciphers, rng.randint(8, len(TLSFingerprint._ciphers))
        )
        ex = rng.sample(TLSFingerprint._ext, rng.randint(6, len(TLSFingerprint._ext)))
        groups = rng.sample([29, 23, 24, 25, 256, 257], rng.randint(3, 6))
        formats = [0]
        raw = ",".join(
            map(
                str,
                [
                    ver,
                    "-".join(map(str, sel)),
                    "-".join(map(str, ex)),
                    "-".join(map(str, groups)),
                    "-".join(map(str, formats)),
                ],
            )
        )
        return hashlib.md5(raw.encode()).hexdigest()
