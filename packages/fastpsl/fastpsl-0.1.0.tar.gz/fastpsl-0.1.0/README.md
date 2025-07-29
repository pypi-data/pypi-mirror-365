# fastpsl

FastPSL is a Python library implemented in Rust with PyO3 bindings, based on Mozilla's PublicSuffixList algorithm. It provides efficient domain parsing functionality, automatically downloads the latest public suffix database (`public_suffix_list.dat`), and exposes a C extension interface via PyO3. It is approximately **four times faster** than the native Python implementation of `tldextract`.

## Usage

```shell
pip install fastpsl
```

```python
>>> import fastpsl

>>> fastpsl.extract("api.example.com")
ExtractResult(subdomain='api', domain='example', suffix='com', is_private=false)

>>> fastpsl.extract("https://sub.domain.example.com:8000/path?query=123")
ExtractResult(subdomain='sub.domain', domain='example', suffix='com', is_private=false)
```

## Contributing

This project is actively being developed, and all forms of participation are welcome.

## License

MIT License
