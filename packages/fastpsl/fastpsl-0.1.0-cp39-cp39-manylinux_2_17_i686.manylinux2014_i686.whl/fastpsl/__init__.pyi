from dataclasses import dataclass

class ExtractResult(dataclass):
    subdomain: str
    domain: str
    suffix: str
    is_private: bool

def extract(domain: str | bytes) -> ExtractResult: ...
