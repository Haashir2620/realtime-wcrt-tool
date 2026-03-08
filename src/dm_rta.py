import math

import math


def compute_wcrt_dm(tasks):
    """
    Deadline Monotonic (DM) Response Time Analysis (RTA).

    tasks: list of Task objects with fields: C, T, D
    Returns: list of dicts, each with:
        name, R, schedulable, D
    """

    # DM priority order: smaller deadline => higher priority
    tasks_sorted = sorted(tasks, key=lambda t: t.D)

    results = []

    for i, task in enumerate(tasks_sorted):
        # Higher-priority tasks are those before index i
        hp = tasks_sorted[:i]

        # Start R with own execution time
        R = task.C

        while True:
            interference = 0.0
            for h in hp:
                # how many jobs of h can execute during R
                interference += math.ceil(R / h.T) * h.C

            R_next = task.C + interference

            # Fixed point reached
            if R_next == R:
                break

            # If we already exceed deadline, we can stop
            if R_next > task.D:
                R = R_next
                break

            R = R_next

        results.append({
            "name": task.name,
            "R": R,
            "D": task.D,
            "schedulable": (R <= task.D),
        })

    return results
