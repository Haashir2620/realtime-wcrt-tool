import sys
import math
import csv
import os
from datetime import datetime

from csv_loader import load_tasks_from_csv
from dm_rta import compute_wcrt_dm
from simulator import simulate_dm, simulate_edf
from edf_pda import edf_schedulable_pda


def save_results(results, sim, path, time_limit, run_id, filename, algo_name):
    os.makedirs("results", exist_ok=True)
    out_path = os.path.join("results", filename)

    write_header = not os.path.exists(out_path)

    with open(out_path, "a", newline="") as f:
        w = csv.writer(f)

        if write_header:
            w.writerow([
                "run_id",
                "input_file",
                "time_limit",
                "algorithm",
                "task",
                "RTA_WCRT_raw",
                "RTA_WCRT_ceil",
                "max_observed_rt",
                "deadline_misses"
            ])

        for r in results:
            name = r["name"]
            rta_raw = r["R"]
            rta_ceil = math.ceil(rta_raw)

            rts = sim["response_times"].get(name, [])
            max_rt = max(rts) if rts else None
            misses = sim["deadline_misses"].get(name, 0)

            w.writerow([
                run_id,
                path,
                time_limit,
                algo_name,
                name,
                f"{rta_raw:.2f}",
                rta_ceil,
                max_rt,
                misses
            ])

    print(f"Saved results to: {out_path}")


def main():
    # CLI:
    # python src/main.py <path_to_csv> <time_limit>
    path = sys.argv[1] if len(sys.argv) > 1 else "tasks/case_ok.csv"
    time_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 200000

    run_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Project says: deadlines <= periods
    tasks = load_tasks_from_csv(path, require_deadline_le_period=True)

    # ----------------------------
    # 1) DM ANALYSIS (RTA)
    # ----------------------------
    print("\n===== DM ANALYSIS (RTA) =====")
    dm_results = compute_wcrt_dm(tasks)

    dm_all_ok = True
    for r in dm_results:
        status = "OK" if r["schedulable"] else "MISS"
        if not r["schedulable"]:
            dm_all_ok = False
        print(f'{r["name"]}: R={r["R"]:.2f}, D={r["D"]:.2f} -> {status}')

    print(f"DM schedulability (all tasks): {'OK' if dm_all_ok else 'MISS'}")

    # ----------------------------
    # 2) EDF ANALYSIS (PDA)
    # ----------------------------
    print("\n===== EDF ANALYSIS (Processor Demand) =====")
    edf_ok, worst_slack, worst_t = edf_schedulable_pda(tasks)
    print(f"EDF schedulability: {'OK' if edf_ok else 'MISS'} "
          f"(worst_slack={worst_slack:.2f} at t={worst_t})")

    # ----------------------------
    # 3) DM SIMULATION
    # ----------------------------
    print("\n===== DM SIMULATION =====")
    dm_sim = simulate_dm(tasks, time_limit=time_limit)

    for r in dm_results:
        name = r["name"]
        rts = dm_sim["response_times"][name]
        max_rt = max(rts) if rts else None
        misses = dm_sim["deadline_misses"][name]
        print(f"{name}: max_rt={max_rt}, deadline_misses={misses}")

    save_results(
        dm_results,
        dm_sim,
        path,
        time_limit,
        run_id,
        "run_results_dm.csv",
        "DM"
    )

    # ----------------------------
    # 4) EDF SIMULATION
    # ----------------------------
    print("\n===== EDF SIMULATION =====")
    edf_sim = simulate_edf(tasks, time_limit=time_limit)

    for r in dm_results:  # reuse same task names/order
        name = r["name"]
        rts = edf_sim["response_times"][name]
        max_rt = max(rts) if rts else None
        misses = edf_sim["deadline_misses"][name]
        print(f"{name}: max_rt={max_rt}, deadline_misses={misses}")

    save_results(
        dm_results,   # keep DM RTA in file for comparison vs observed EDF RT
        edf_sim,
        path,
        time_limit,
        run_id,
        "run_results_edf.csv",
        "EDF"
    )

    print("\nRun completed.")
    print(f"Run ID: {run_id}")


if __name__ == "__main__":
    main()