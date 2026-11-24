#!/usr/bin/env python3
"""Genera MD5 (-m 0), NTLM (-m 1000) y bcrypt (-m 3200) del fichero de entrada."""
import argparse, hashlib, sys

ap = argparse.ArgumentParser()
ap.add_argument("wordlist")
ap.add_argument("--md5", default="md5.txt")
ap.add_argument("--ntlm", default="ntlm.txt")
ap.add_argument("--bcrypt", default="bcrypt.txt")
ap.add_argument("--bcrypt-n", type=int, default=2000)
ap.add_argument("--bcrypt-rounds", type=int, default=10)
a = ap.parse_args()

from passlib.hash import nthash
pws = [l.rstrip("\r\n") for l in open(a.wordlist, encoding="utf-8")]
pws = [p for p in pws if p]

with open(a.md5, "w") as fm, open(a.ntlm, "w") as fn:
    for pw in pws:
        fm.write(hashlib.md5(pw.encode("utf-8")).hexdigest() + "\n")
        fn.write(nthash.hash(pw) + "\n")
print(f"MD5 -> {a.md5} ({len(pws):,})", file=sys.stderr)
print(f"NTLM -> {a.ntlm} ({len(pws):,})", file=sys.stderr)

if a.bcrypt_n:
    import bcrypt as B
    with open(a.bcrypt, "w") as fb:
        for pw in pws[:a.bcrypt_n]:
            fb.write(B.hashpw(pw.encode("utf-8")[:72], B.gensalt(rounds=a.bcrypt_rounds)).decode() + "\n")
    print(f"bcrypt -> {a.bcrypt} ({min(a.bcrypt_n,len(pws)):,}, cost={a.bcrypt_rounds})", file=sys.stderr)
