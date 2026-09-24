#!/usr/bin/env python3
"""Fetch a deterministic set of dbSNP esummary XML records and save them
under `tests/fixtures/dbsnp/` for offline testing.

Run locally (one-off):

    python tools/generate_dbsnp_fixtures.py

"""
import os
import random
import time
import urllib.request


OUTDIR = os.path.join("tests", "fixtures", "dbsnp")
os.makedirs(OUTDIR, exist_ok=True)


def _fetch(snp_id: int) -> str | None:
    url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        f"?db=snp&id={snp_id}&report=Brief&retmode=xml"
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"fetch error for {snp_id}: {e}")
        return None


def main():
    random.seed(42)
    ids = [random.randint(1, 20_000_000) for _ in range(100)]

    saved = 0
    for snp_id in ids:
        xml = _fetch(snp_id)
        # be polite
        time.sleep(0.15)
        if not xml:
            continue
        if "<DocumentSummary" not in xml:
            continue
        path = os.path.join(OUTDIR, f"{snp_id}.xml")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(xml)
        print("saved", path)
        saved += 1
        if saved >= 12:
            break

    print(f"done — saved {saved} fixtures to {OUTDIR}")


if __name__ == "__main__":
    main()
