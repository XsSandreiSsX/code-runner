# range_subarray_sum

ACCEPTED = """
MOD = 1000000007

n, q = map(int, input().split())
a = list(map(int, input().split()))

pref0 = [0] * (n + 1)
pref1 = [0] * (n + 1)
pref2 = [0] * (n + 1)
pref3 = [0] * (n + 1)

for i in range(1, n + 1):
    x = a[i - 1] % MOD

    pref0[i] = (pref0[i - 1] + x) % MOD
    pref1[i] = (pref1[i - 1] + x * i) % MOD
    pref2[i] = (pref2[i - 1] + x * (i + 1)) % MOD
    pref3[i] = (pref3[i - 1] + x * i * (i + 1)) % MOD

answers = []

for _ in range(q):
    l, r = map(int, input().split())

    s0 = (pref0[r] - pref0[l - 1]) % MOD
    s1 = (pref1[r] - pref1[l - 1]) % MOD
    s2 = (pref2[r] - pref2[l - 1]) % MOD
    s3 = (pref3[r] - pref3[l - 1]) % MOD

    left_part = (s2 - l * s0) % MOD
    right_part = (s3 - l * s1) % MOD

    ans = ((r + 1) * left_part - right_part) % MOD
    answers.append(ans)

for ans in answers:
    print(ans)
"""

WRONG_ANSWER = """
MOD = 1000000007

n, q = map(int, input().split())
a = list(map(int, input().split()))

pref = [0] * (n + 1)

for i in range(1, n + 1):
    pref[i] = (pref[i - 1] + a[i - 1]) % MOD

for _ in range(q):
    l, r = map(int, input().split())
    print((pref[r] - pref[l - 1]) % MOD)
"""

TIME_LIMIT_EXCEEDED = """
MOD = 1000000007

n, q = map(int, input().split())
a = list(map(int, input().split()))

for _ in range(q):
    l, r = map(int, input().split())
    l -= 1
    r -= 1

    ans = 0

    for left in range(l, r + 1):
        cur_sum = 0

        for right in range(left, r + 1):
            cur_sum += a[right]
            ans += cur_sum

    print(ans % MOD)
"""

MEMORY_LIMIT_EXCEEDED = """
import sys

n, q = map(int, input().split())
a = list(map(int, input().split()))

bloat = [0] * 80_000_000
print(bloat[40_000_000])

for _ in range(q):
    l, r = map(int, input().split())
    print(0)
"""

RUNTIME_ERROR = """
n, q = map(int, input().split())
a = list(map(int, input().split()))

print(a[n])
"""

COMPILATION_ERROR = """
MOD = 1000000007

n, q = map(int, input().split())
a = list(map(int, input().split()))

print(a[0] + )
"""
