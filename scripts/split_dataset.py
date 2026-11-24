#!/usr/bin/env python3
"""Deduplica, baraja (semilla fija) y divide un corpus en train/test DISJUNTOS."""
import argparse, random, sys

ap = argparse.ArgumentParser()
ap.add_argument("corpus")
ap.add_argument("--train", default="train.txt")
ap.add_argument("--test", default="test.txt")
ap.add_argument("--test-frac", type=float, default=0.2)
ap.add_argument("--seed", type=int, default=42)
ap.add_argument("--min-len", type=int, default=1)
ap.add_argument("--max-len", type=int, default=64)
ap.add_argument("--ascii-only", action="store_true")
a = ap.parse_args()

seen, uniq, kept, dropped = set(), [], 0, 0
with open(a.corpus, encoding="latin-1") as f:
    for line in f:
        pw = line.rstrip("\r\n")
        if not (a.min_len <= len(pw) <= a.max_len): dropped += 1; continue
        if a.ascii_only and (not pw.isascii() or not pw.isprintable()): dropped += 1; continue
        if pw in seen: continue
        seen.add(pw); uniq.append(pw); kept += 1

random.seed(a.seed); random.shuffle(uniq)
n = int(len(uniq) * a.test_frac)
test, train = uniq[:n], uniq[n:]
open(a.train, "w", encoding="utf-8").write("\n".join(train) + "\n")
open(a.test, "w", encoding="utf-8").write("\n".join(test) + "\n")
print(f"Unicas: {kept:,} (descartadas: {dropped:,})", file=sys.stderr)
print(f"Train: {len(train):,} -> {a.train}", file=sys.stderr)
print(f"Test:  {len(test):,} -> {a.test}", file=sys.stderr)
