#!/usr/bin/env python3
"""SKYNET 1_1_0 — NATIVE RUNTIME PERFORMANCE / STRESS TEST 01 — PUBLICATION COPY
10 independent native-runtime measurement runs.
No direct succession, no manual descendant attachment, no monkey-patching,
no precomputed performance result and no performance PASS threshold.
"""
from __future__ import annotations
import asyncio, hashlib, importlib.util, json, math, os, platform, statistics, sys, time
from datetime import datetime, timezone
from pathlib import Path

SOURCE=Path("BORN_OF_THE_DARK_ABYSS_FINAL_1_1_0.py")
RESULT=Path("SKYNET_NATIVE_RUNTIME_STRESS_01_RESULT_1_1_0.txt")
RUNS=10
CYCLES_PER_RUN=43
SEQUENCE="ATGC"*16

def identity(p):
    b=p.read_bytes(); t=b.decode()
    return {"path":str(p.resolve()),"lines":len(t.splitlines()),"characters":len(t),
            "bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}

def load(p):
    spec=importlib.util.spec_from_file_location("skynet_stress_target",p)
    if spec is None or spec.loader is None: raise RuntimeError("source import failed")
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m
    spec.loader.exec_module(m); return m

def pct(v,q):
    a=sorted(v)
    if len(a)==1:return a[0]
    x=(len(a)-1)*q; lo=math.floor(x); hi=math.ceil(x)
    return a[lo] if lo==hi else a[lo]*(hi-x)+a[hi]*(x-lo)

def rate(n,s): return n/s if s>0 else 0.0

async def run_once(m,n):
    initial=m.ENGINP2Core(); eng=initial.engin; rows=[]
    run0=time.perf_counter_ns(); first_event_cycle=None; first_event_s=None
    for c in range(1,CYCLES_PER_RUN+1):
        before=len(eng.cores)
        kw={"nucleotide_sequences":{initial.core_id:SEQUENCE}} if c==1 else {}
        t0=time.perf_counter_ns()
        out=await eng.requiem_execution_cycle(**kw)
        t1=time.perf_counter_ns()
        dt=(t1-t0)/1e9; after=len(eng.cores)
        inter=len(out["harmonic_interactions"]); res=len(out["resonance_states"])
        desc=len(out["descendants"]); ss=len(out["succession_states"])
        gen=max(x.generation for x in eng.cores)
        if desc and first_event_cycle is None:
            first_event_cycle=c; first_event_s=(t1-run0)/1e9
        row={"cycle":c,"latency_s":dt,"cores_before":before,"cores_after":after,
             "new_cores":after-before,"max_generation":gen,"samples":len(out["samples"]),
             "interactions":inter,"resonances":res,"succession_states":ss,
             "descendants":desc,"cycles_per_s":rate(1,dt),
             "interactions_per_s":rate(inter,dt),"resonances_per_s":rate(res,dt)}
        rows.append(row)
        print(f"RUN={n:02d} CYCLE={c:03d} TIME={dt:.9f}s "
              f"CORES={before}->{after} NEW={after-before} GEN={gen} "
              f"INTERACTIONS={inter} RESONANCE={res} DESCENDANTS={desc} "
              f"IPS={rate(inter,dt):.3f}")
    total=(time.perf_counter_ns()-run0)/1e9
    lat=[x["latency_s"] for x in rows]
    ti=sum(x["interactions"] for x in rows); tr=sum(x["resonances"] for x in rows)
    td=sum(x["descendants"] for x in rows)
    return {"run":n,"total_s":total,"cycles":len(rows),"final_cores":len(eng.cores),
            "max_generation":max(x.generation for x in eng.cores),
            "total_interactions":ti,"total_resonances":tr,"total_descendants":td,
            "first_succession_cycle":first_event_cycle,
            "first_succession_latency_s":first_event_s,
            "latency_min_s":min(lat),"latency_mean_s":statistics.fmean(lat),
            "latency_median_s":statistics.median(lat),"latency_p95_s":pct(lat,.95),
            "latency_p99_s":pct(lat,.99),"latency_max_s":max(lat),
            "cycles_per_s":rate(len(rows),total),"interactions_per_s":rate(ti,total),
            "resonances_per_s":rate(tr,total),"cycles_raw":rows}

async def main():
    if not SOURCE.is_file(): raise FileNotFoundError(SOURCE)
    sid=identity(SOURCE); m=load(SOURCE)
    print("="*78); print("SKYNET 1_1_0 — NATIVE RUNTIME PERFORMANCE / STRESS TEST 01")
    print("="*78)
    print("STARTED_UTC       =",datetime.now(timezone.utc).isoformat())
    print("PLATFORM          =",platform.platform()); print("PYTHON            =",platform.python_version())
    print("CPU_COUNT         =",os.cpu_count()); print("RUNS              =",RUNS)
    print("CYCLES_PER_RUN    =",CYCLES_PER_RUN); print("SEQUENCE_LENGTH   =",len(SEQUENCE))
    print("SOURCE_LINES      =",sid["lines"]); print("SOURCE_CHARACTERS =",sid["characters"])
    print("SOURCE_BYTES      =",sid["bytes"]); print("SOURCE_SHA256     =",sid["sha256"])
    runs=[]
    for n in range(1,RUNS+1):
        print("\n"+"="*78+f"\nRUN {n:02d}/{RUNS:02d}\n"+"="*78)
        runs.append(await run_once(m,n))
    lat=[x["latency_s"] for r in runs for x in r["cycles_raw"]]
    tc=sum(r["cycles"] for r in runs); ts=sum(r["total_s"] for r in runs)
    ti=sum(r["total_interactions"] for r in runs); tr=sum(r["total_resonances"] for r in runs)
    td=sum(r["total_descendants"] for r in runs)
    summary={"benchmark":"SKYNET_NATIVE_RUNTIME_STRESS_01_1_1_0",
      "completed_runs":len(runs),"cycles_per_run":CYCLES_PER_RUN,"total_cycles":tc,
      "measured_runtime_s":ts,"total_interactions":ti,"total_resonances":tr,
      "total_descendants":td,"aggregate_cycles_per_s":rate(tc,ts),
      "aggregate_interactions_per_s":rate(ti,ts),"aggregate_resonances_per_s":rate(tr,ts),
      "cycle_latency_min_s":min(lat),"cycle_latency_mean_s":statistics.fmean(lat),
      "cycle_latency_median_s":statistics.median(lat),"cycle_latency_p95_s":pct(lat,.95),
      "cycle_latency_p99_s":pct(lat,.99),"cycle_latency_max_s":max(lat),
      "source":sid,"environment":{"platform":platform.platform(),
      "python":platform.python_version(),"cpu_count":os.cpu_count()},"runs":runs}
    RESULT.write_text("SKYNET 1_1_0 — NATIVE RUNTIME PERFORMANCE / STRESS TEST 01\n"
                      "RAW MEASUREMENT RESULT\n"+"="*78+"\n"+
                      json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("\n"+"="*78+"\nAGGREGATE MEASURED RESULT\n"+"="*78)
    for k in ("completed_runs","total_cycles","measured_runtime_s","total_interactions",
              "total_resonances","total_descendants","aggregate_cycles_per_s",
              "aggregate_interactions_per_s","aggregate_resonances_per_s",
              "cycle_latency_min_s","cycle_latency_mean_s","cycle_latency_median_s",
              "cycle_latency_p95_s","cycle_latency_p99_s","cycle_latency_max_s"):
        print(f"{k.upper():28s} = {summary[k]}")
    print("RESULT_FILE                  =",RESULT); print("="*78)

if __name__=="__main__":
    asyncio.run(main())
