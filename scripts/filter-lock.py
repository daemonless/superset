#!/usr/bin/env python3
"""Filter upstream's requirements lock against pkg-provided packages.

Reads /tmp/base-lock.txt (superset's pip-compiled requirements/base.txt)
and /app/constraints.txt (pip freeze of the pkg-provided site-packages),
writes /tmp/requirements-locked.txt: the lock minus everything FreeBSD
packages already provide, with overrides for entries that would need a
compiler to build.
"""

import re

# Deviations from the lock (would need cc/rust to build):
OVERRIDES = {
    "pygeohash": "pygeohash<3",  # 3.x grew a C extension; 2.x is pure
}


def norm(name):
    return re.sub(r"[-_.]+", "-", name).lower()


system = set()
for line in open("/app/constraints.txt"):
    m = re.match(r"([A-Za-z0-9_.-]+)==", line)
    if m:
        system.add(norm(m.group(1)))

out = []
for line in open("/tmp/base-lock.txt"):
    line = line.strip()
    if not line or line.startswith(("#", "-e ", "--")):
        continue
    m = re.match(r"([A-Za-z0-9_.-]+)(\[[^]]*\])?==(.+)", line)
    if not m:
        continue
    name = norm(m.group(1))
    if name in system:
        continue
    out.append(OVERRIDES.get(name, line))

with open("/tmp/requirements-locked.txt", "w") as f:
    f.write("\n".join(out) + "\n")
print(f"locked requirements: {len(out)} to install, "
      f"{len(system)} provided by packages")
