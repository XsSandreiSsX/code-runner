# a_plus_b

ACCEPTED = """
a, b = map(int, input().split())
print(a + b)
"""

WRONG_ANSWER = """
a, b = map(int, input().split())
print(abs(a + b))
"""

TIME_LIMIT_EXCEEDED = """
while True:
    pass
"""

MEMORY_LIMIT_EXCEEDED = """
import sys

a, b = map(int, input().split())

bloat = [0] * 20_000_000
print(bloat[10_000_000])

print(a + b)
"""

RUNTIME_ERROR = """
a, b = map(int, input().split())
print(a / 0)
"""

COMPILATION_ERROR = """
a, b = map(int, input().split())
print(a + )
"""
