#!/usr/bin/env python3
"""Trace-driven reference model for the 1 KiB direct-mapped cache.
This is an architectural model, NOT an RTL simulation. Timing assumptions are
explicit command-line parameters and must not be presented as measured Fmax.
"""
import argparse, csv, json, random
from pathlib import Path

LINES, BLOCK_BYTES, WORD_BYTES, DEFAULT_N, SEED = 64, 16, 4, 1024, 20261114

def workloads(n):
    rng = random.Random(SEED)
    return {
        "sequential": [((i % 256) * WORD_BYTES) for i in range(n)],
        "repeated": [((i % 4) * WORD_BYTES) for i in range(n)],
        "random": [rng.randrange(1024) * WORD_BYTES for _ in range(n)],
        "conflict_heavy": [(0 if i % 2 == 0 else 64) * BLOCK_BYTES for i in range(n)],
    }

def run(trace, hit_time, miss_penalty):
    tags, valid = [None] * LINES, [False] * LINES
    hits = misses = 0
    for addr in trace:
        block = addr // BLOCK_BYTES
        index, tag = block % LINES, block // LINES
        if valid[index] and tags[index] == tag:
            hits += 1
        else:
            misses += 1
            valid[index], tags[index] = True, tag
    total = len(trace)
    miss_rate = misses / total
    amat = hit_time + miss_rate * miss_penalty
    return {"accesses": total, "hits": hits, "misses": misses,
            "hit_rate": hits / total, "miss_rate": miss_rate,
            "amat_cycles": amat, "uncached_baseline_cycles": miss_penalty,
            "estimated_speedup": miss_penalty / amat}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--accesses", type=int, default=DEFAULT_N)
    p.add_argument("--hit-time", type=float, default=1.0)
    p.add_argument("--miss-penalty", type=float, default=5.0)
    p.add_argument("--out", default="sim/trace_benchmark")
    a = p.parse_args()
    if a.accesses < 1 or a.hit_time < 0 or a.miss_penalty <= 0:
        p.error("accesses and miss penalty must be positive; hit time cannot be negative")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    summary = {}
    for name, trace in workloads(a.accesses).items():
        summary[name] = run(trace, a.hit_time, a.miss_penalty)
        with (out / (name + ".csv")).open("w", newline="") as f:
            w = csv.writer(f); w.writerow(["address_hex", "operation"])
            w.writerows((f"0x{x:08X}", "READ") for x in trace)
    fields = ["workload", "accesses", "hits", "misses", "hit_rate",
              "miss_rate", "amat_cycles", "uncached_baseline_cycles", "estimated_speedup"]
    with (out / "summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for name, result in summary.items(): w.writerow({"workload": name, **result})
    meta = {"model": "architectural reference model; not RTL simulation",
            "cache_bytes": 1024, "lines": LINES, "block_bytes": BLOCK_BYTES,
            "words_per_block": 4, "address_bits": 32, "accesses_per_trace": a.accesses,
            "random_seed": SEED, "assumed_hit_time_cycles": a.hit_time,
            "assumed_miss_penalty_cycles": a.miss_penalty,
            "amat": "hit_time + miss_rate * miss_penalty",
            "uncached_baseline": "one main-memory access per request; latency=miss_penalty",
            "results": summary}
    (out / "summary.json").write_text(json.dumps(meta, indent=2) + "\n")
    print("ARCHITECTURAL TRACE MODEL — NOT RTL CYCLE MEASUREMENTS")
    print(f"Assumptions: hit={a.hit_time:g} cycles; miss penalty={a.miss_penalty:g} cycles; seed={SEED}")
    print(f"{'Workload':<17} {'Hits':>6} {'Misses':>7} {'Hit %':>8} {'AMAT':>8} {'Speedup':>9}")
    for name, r in summary.items():
        print(f"{name:<17} {r['hits']:>6} {r['misses']:>7} {100*r['hit_rate']:>7.2f}% {r['amat_cycles']:>8.3f} {r['estimated_speedup']:>8.3f}x")
    print("Trace CSV and summary files:", out)

if __name__ == "__main__": main()
