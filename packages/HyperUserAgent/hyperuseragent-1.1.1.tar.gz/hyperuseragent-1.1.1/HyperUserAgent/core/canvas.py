import random, base64, hashlib, io, PIL.Image, PIL.ImageDraw, PIL.ImageFont


class CanvasFingerprint:
    """
    Simulate Canvas rendering differences → SHA-256 of pixel buffer.
    """

    @staticmethod
    def simulate(rng: random.Random) -> str:
        w, h = 220, 30
        img = PIL.Image.new("RGB", (w, h), (255, 255, 255))
        d = PIL.ImageDraw.Draw(img)
        fnt = PIL.ImageFont.load_default()
        txt = "Hyper-UA " + str(rng.random())
        d.text(
            (10, 5),
            txt,
            font=fnt,
            fill=(rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255)),
        )
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return hashlib.sha256(buf.getvalue()).hexdigest()
