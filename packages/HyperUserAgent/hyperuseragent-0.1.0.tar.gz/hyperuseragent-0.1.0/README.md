# HyperUserAgent

**HyperUserAgent** (Hyper-UA) is an advanced Python package for generating ultra-realistic User-Agent strings and browser fingerprints.  
Built for stealth web scraping, testing, and automation, it simulates real browsers and platforms with high fidelity, including dynamic TLS fingerprints, HTTP/2 settings, canvas/webgl hashes, proxy rotation, and behavioural biometrics.

## Features

- Generate statistically weighted User-Agent strings mimicking real browser market shares (StatCounter 2025)  
- Supports major browsers: Chrome, Firefox, Safari, Edge, Opera, Brave, Yandex  
- Target multiple platforms: desktop, mobile, tablet with accurate OS and device modeling  
- Support for browser release channels: stable, beta, dev, canary (where applicable)  
- Match real version trains and engine tokens (e.g., CriOS for Chrome on iOS)  
- Full fingerprint simulation: Canvas, WebGL, TLS JA3 hashes, HTTP/2 frames  
- Behavioral biometrics simulation for human-like delays and interactions  
- Proxy rotation with sticky sessions  
- Machine learning based anomaly detection to detect bot-detection signals  
- Drop-in requests-compatible HTTP client (`HyperSession`) with UA and proxy rotation  
- Fully typed, dependency-minimal, and production-ready

---

## Installation

Requires Python 3.9 or later.

```
pip install HyperUserAgent
```

---

## Quick Start

```python
from HyperUserAgent import HyperUA

# Create a HyperUA instance
ua_generator = HyperUA()

# Generate a realistic desktop User-Agent string
ua = ua_generator.create(platform="desktop")
print(ua)

# Generate a mobile Chrome User-Agent
mobile_chrome_ua = ua_generator.create(platform="mobile", browser="chrome")
print(mobile_chrome_ua)

# Using default parameters (random platform and browser weighted by market share)
random_ua = ua_generator.random()
print(random_ua)

# Generate a Chrome Browser User-Agent
chrome_ua = ua_generator.chrome()
print(chrome_ua)
```

---

## API Reference

### `HyperUA.create(platform='desktop', browser=None, channel=None, min_version=None) -> str`

Generates a realistic User-Agent string with optional controls:

- **platform** (`'desktop'`, `'mobile'`, `'tablet'`): Device platform to emulate.  
- **browser** (`'chrome'`, `'firefox'`, `'safari'`, `'edge'`, `'opera'`, `'brave'`, `'yandex'`): Browser to emulate.  
- **channel** (`'stable'`, `'beta'`, `'dev'`, `'canary'`): Release channel; affects version selection but not UA format.  
- **min_version** (`str`): Minimum browser version, e.g., `"120.0"`.

Returns a full User-Agent string matching authentic browser behaviors.

### `Fingerprint.generate(ua: str, seed=None) -> Fingerprint`

Generates fingerprint components that align with the User-Agent string for realistic anti-bot evasion.

### `HyperSession`

An HTTP client with automatic User-Agent rotation, proxy handling, TLS & HTTP/2 fingerprinting, and human-like throttling.

### `ProxyPool`

Proxy manager supporting sticky sessions and rotation from JSON proxy lists.

---

## Contributing

Contributions, bug reports, and feature requests are welcome via GitHub issues and pull requests.

---

## License

This project is licensed under the MIT License — free for personal, academic, and commercial use.

---