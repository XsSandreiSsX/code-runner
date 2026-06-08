# segment_tree_sum

ACCEPTED = """
import sys

input = sys.stdin.readline


class SegmentTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, v, tl, tr):
        if tl == tr:
            self.tree[v] = arr[tl]
            return

        tm = (tl + tr) // 2
        self._build(arr, v * 2, tl, tm)
        self._build(arr, v * 2 + 1, tm + 1, tr)
        self.tree[v] = self.tree[v * 2] + self.tree[v * 2 + 1]

    def update(self, pos, value, v=1, tl=0, tr=None):
        if tr is None:
            tr = self.n - 1

        if tl == tr:
            self.tree[v] = value
            return

        tm = (tl + tr) // 2

        if pos <= tm:
            self.update(pos, value, v * 2, tl, tm)
        else:
            self.update(pos, value, v * 2 + 1, tm + 1, tr)

        self.tree[v] = self.tree[v * 2] + self.tree[v * 2 + 1]

    def query(self, l, r, v=1, tl=0, tr=None):
        if tr is None:
            tr = self.n - 1

        if l > r:
            return 0

        if l == tl and r == tr:
            return self.tree[v]

        tm = (tl + tr) // 2

        return (
            self.query(l, min(r, tm), v * 2, tl, tm)
            + self.query(max(l, tm + 1), r, v * 2 + 1, tm + 1, tr)
        )


n, q = map(int, input().split())
a = list(map(int, input().split()))

seg = SegmentTree(a)
answers = []

for _ in range(q):
    query = list(map(int, input().split()))

    if query[0] == 1:
        _, i, x = query
        seg.update(i - 1, x)
    else:
        _, l, r = query
        answers.append(str(seg.query(l - 1, r - 1)))

print("\\n".join(answers))
"""

WRONG_ANSWER = """
import sys

input = sys.stdin.readline

n, q = map(int, input().split())
a = list(map(int, input().split()))

answers = []

for _ in range(q):
    query = list(map(int, input().split()))

    if query[0] == 1:
        _, i, x = query
        a[i - 1] = x
    else:
        _, l, r = query
        answers.append(str(sum(a[l:r])))

print("\\n".join(answers))
"""

TIME_LIMIT_EXCEEDED = """
import sys

input = sys.stdin.readline

n, q = map(int, input().split())
a = list(map(int, input().split()))

answers = []

for _ in range(q):
    query = list(map(int, input().split()))

    if query[0] == 1:
        _, i, x = query
        a[i - 1] = x
    else:
        _, l, r = query

        total = 0
        for i in range(l - 1, r):
            total += a[i]

        answers.append(str(total))

print("\\n".join(answers))
"""

MEMORY_LIMIT_EXCEEDED = """
import sys

n, q = map(int, input().split())
a = list(map(int, input().split()))

bloat = [0] * 80_000_000
print(bloat[40_000_000])

for _ in range(q):
    query = list(map(int, input().split()))

    if query[0] == 2:
        print(0)
"""

RUNTIME_ERROR = """
n, q = map(int, input().split())
a = list(map(int, input().split()))

print(a[n])
"""

COMPILATION_ERROR = """
n, q = map(int, input().split())
a = list(map(int, input().split()))

print(a[0] + )
"""