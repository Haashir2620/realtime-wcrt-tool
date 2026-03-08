import math


def dbf_task(t, C, T, D):
    """
    Demand Bound Function for one task i at time t:
      dbf_i(t) = max(0, floor((t - D)/T) + 1) * C
    Assumes D <= T (as in the project requirement).
    """
    if t < D:
        return 0.0
    n_jobs = math.floor((t - D) / T) + 1
    return n_jobs * C


def edf_schedulable_pda(tasks):
    """
    EDF schedulability test using the Processor Demand Approach (PDA)
    for periodic tasks with deadlines <= periods.

    Returns:
      (schedulable: bool, worst_slack: float, worst_t: int)

    Interpretation:
      For EDF to be schedulable, we need:
        sum_i dbf_i(t) <= t   for all relevant t > 0

      slack(t) = t - sum_i dbf_i(t)
      If slack(t) becomes negative => not schedulable.
    """

    # We assume integer-ish timing in your simulator anyway
    # but tasks may be float; we convert to ints for the PDA scan.
    # If your CSVs have integer periods/deadlines/WCET, this is perfect.
    norm = []
    for task in tasks:
        C = float(task.C)
        T = float(task.T)
        D = float(task.D)
        norm.append((C, T, D))

    # --- Choose a finite set of candidate t values ---
    # Standard approach: only need to check t values where dbf changes,
    # i.e., at absolute deadlines: t = k*T + D
    # We check those t up to a horizon.
    #
    # Practical horizon choice for mini-project:
    #   H = lcm of periods (hyperperiod) (if not too huge)
    # If lcm explodes, cap it.
    periods = [int(round(T)) for (_, T, _) in norm]
    if any(p <= 0 for p in periods):
        raise ValueError("All periods must be > 0 for EDF PDA.")

    def lcm(a, b):
        return abs(a * b) // math.gcd(a, b)

    H = 1
    for p in periods:
        H = lcm(H, p)
        if H > 200000:  # cap to avoid insane scans
            H = 200000
            break

    candidate_ts = set()
    for (C, T, D) in norm:
        T_i = int(round(T))
        D_i = int(round(D))
        if D_i <= 0 or T_i <= 0:
            continue
        # k such that k*T + D <= H
        k_max = (H - D_i) // T_i
        for k in range(k_max + 1):
            candidate_ts.add(k * T_i + D_i)

    candidate_ts.discard(0)
    candidate_ts = sorted(candidate_ts)

    worst_slack = float("inf")
    worst_t = None

    for t in candidate_ts:
        demand = 0.0
        for (C, T, D) in norm:
            demand += dbf_task(t, C, T, D)

        slack = t - demand
        if slack < worst_slack:
            worst_slack = slack
            worst_t = t

        if demand > t + 1e-9:  # small epsilon
            return (False, worst_slack, worst_t)

    return (True, worst_slack, worst_t)