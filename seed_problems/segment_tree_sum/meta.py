# segment_tree_sum

TITLE = "Segment Tree Sum"

TIME_LIMIT = 2
MEMORY_LIMIT = 512

STATEMENT = """
You are given an array `a` of length `n`.

There are `q` queries. Each query has one of two types:

`1 i x` — set `a[i] = x`.

`2 l r` — find the sum of elements on the segment `[l, r]`.

All indexes are 1-based.
"""

INPUT = """
The first line contains two integers `n` and `q` — the length of the array and the number of queries.

The second line contains `n` integers `a1, a2, ..., an`.

Each of the next `q` lines contains one query:

- `1 i x` — set `a[i] = x`
- `2 l r` — find the sum of elements on the segment `[l, r]`

Constraints:

- `1 <= n <= 200000`
- `1 <= q <= 200000`
- `-1000000000 <= ai <= 1000000000`
- `-1000000000 <= x <= 1000000000`
- `1 <= i <= n`
- `1 <= l <= r <= n`
"""

OUTPUT = """
For each query of type `2`, print one integer — the sum of elements on the segment `[l, r]`.

Each answer must be printed on a separate line.
"""