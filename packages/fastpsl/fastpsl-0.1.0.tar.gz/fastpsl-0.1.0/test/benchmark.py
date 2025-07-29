import timeit

import fastpsl  # noqa: F401
import tldextract  # noqa: F401

testcase = "http://foo:bar@home.arpa:12345"

print("run tldextract")
tldextract_time = timeit.timeit(f"tldextract.extract('{testcase}')", number=100_000, globals=globals())

print("run fastpsl")
fastpsl_time = timeit.timeit(f"fastpsl.extract('{testcase}')", number=100_000, globals=globals())

print(f"tldextract_time: {tldextract_time * 1000_000 / 100_000:.6f} us/pre extract")
print(f"fastpsl_time: {fastpsl_time * 1000_000 / 100_000:.6f} us/pre extract")
