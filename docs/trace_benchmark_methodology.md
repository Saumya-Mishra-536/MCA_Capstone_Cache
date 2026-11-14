# Trace-driven cache benchmark

## Purpose and scope
This benchmark supplies the representative sequential, repeated, random, and
conflict-heavy memory-access traces required by Project 6. It uses the project's
1 KiB direct-mapped geometry: 64 lines, 16-byte blocks, four 32-bit words per
block, 32-bit byte addresses. The model implements valid-bit/tag lookup and
allocate-on-miss replacement.

**Important:** the Python program is an architectural reference model, not an
RTL simulator. Its hit/miss counts are deterministic for the generated traces.
AMAT and speedup are estimates based on explicitly stated timing assumptions;
they are not measured RTL cycle counts or FPGA timing results.

## Reproduce
From the repository root:
```sh
python3 sim/trace_benchmark.py --accesses 1024 --hit-time 1 --miss-penalty 5
```
The program writes one CSV trace per workload plus `summary.csv` and
`summary.json` under `sim/trace_benchmark/`. Random trace seed: 20261114.

## Initial reference-model results
With 1-cycle hit-time and 5-cycle miss-penalty assumptions:

| Workload | Accesses | Hits | Misses | Hit rate | Miss rate | AMAT (cycles) | Estimated speedup |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sequential | 1024 | 960 | 64 | 93.75% | 6.25% | 1.3125 | 3.810x |
| Repeated | 1024 | 1023 | 1 | 99.90% | 0.10% | 1.0049 | 4.976x |
| Random | 1024 | 229 | 795 | 22.36% | 77.64% | 4.8823 | 1.024x |
| Conflict-heavy | 1024 | 0 | 1024 | 0.00% | 100.00% | 6.0000 | 0.833x |

Formula: `AMAT = hit_time + miss_rate × miss_penalty`. The uncached baseline
is modeled as one main-memory access per request with latency equal to the
assumed 5-cycle miss penalty. Speedup = baseline latency / AMAT.

## Interpretation
Sequential and repeated traces benefit from spatial and temporal locality.
The random trace has a lower hit rate because its working set exceeds the
cache's 64-block capacity. The conflict-heavy trace alternates two blocks that
map to the same direct-mapped line, causing every access to miss after each
replacement. This demonstrates a direct-mapped conflict-miss limitation.

## Required next validation
Before treating these values as final hardware performance results, replay
these exact traces through a trace-driven Verilog testbench connected to the
actual `cache_top`, measure request-to-`cpu_ready` cycles, and calculate
AMAT from those measured latencies. Keep this reference-model table clearly
labelled as such until that RTL run is completed.
