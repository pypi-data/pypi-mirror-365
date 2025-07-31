from __future__ import annotations
import json, yaml, importlib.resources as r
from functools import lru_cache
from typing import Any, Dict, List


def _load(pkg: str, name: str) -> Any:
    with r.files(pkg).joinpath(name).open("r", encoding="utf-8") as fh:
        return json.load(fh) if name.endswith(".json") else yaml.safe_load(fh)


@lru_cache
def browsers() -> Dict[str, Any]:
    return _load("HyperUserAgent.config", "browsers.json")


@lru_cache
def os_cfg() -> Dict[str, Any]:
    return _load("HyperUserAgent.config", "os.json")


@lru_cache
def weights() -> Dict[str, Any]:
    return _load("HyperUserAgent.config", "weights.yaml")
