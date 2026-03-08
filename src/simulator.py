def simulate_dm(tasks, time_limit):
    """
    Simple preemptive DM simulation (discrete time, 1 time unit step).
    """

    # DM priority: smallest deadline first
    tasks_sorted = sorted(tasks, key=lambda x: x.D)

    active = {t.name: [] for t in tasks_sorted}

    response_times = {t.name: [] for t in tasks_sorted}
    deadline_misses = {t.name: 0 for t in tasks_sorted}
    completed_jobs = {t.name: 0 for t in tasks_sorted}

    for t in range(time_limit):
        # Release jobs
        for task in tasks_sorted:
            if t % int(task.T) == 0:
                active[task.name].append({
                    "release": t,
                    "deadline": t + task.D,
                    "remaining": task.C
                })

        # Deadline misses
        for task in tasks_sorted:
            for job in active[task.name]:
                if t >= job["deadline"] and job["remaining"] > 0:
                    deadline_misses[task.name] += 1
                    job["remaining"] = 0

        # Pick highest-priority ready job
        chosen_task = None
        chosen_job = None

        for task in tasks_sorted:
            for job in active[task.name]:
                if job["remaining"] > 0:
                    chosen_task = task
                    chosen_job = job
                    break
            if chosen_task:
                break

        # Execute 1 time unit
        if chosen_job:
            chosen_job["remaining"] -= 1
            if chosen_job["remaining"] <= 0:
                finish = t + 1
                rt = finish - chosen_job["release"]
                response_times[chosen_task.name].append(rt)
                completed_jobs[chosen_task.name] += 1

        # Cleanup
        for task in tasks_sorted:
            active[task.name] = [j for j in active[task.name] if j["remaining"] > 0]

    return {
        "response_times": response_times,
        "deadline_misses": deadline_misses,
        "completed_jobs": completed_jobs,
        "time_limit": time_limit
    }

def simulate_edf(tasks, time_limit):
    """
    Simple preemptive EDF simulation (discrete time, 1 time unit step).

    EDF rule:
      - At each time t, run the active job with the smallest absolute deadline
        (absolute deadline = release_time + D).

    Assumptions:
      - Periodic tasks
      - Releases at multiples of T
      - Preemptive, single core
      - Discrete time steps of 1
      - Execution time uses task.C (WCET)
    """

    # We don't sort tasks for priority (EDF is dynamic), but sorting helps stable iteration
    tasks_list = list(tasks)

    # Active jobs stored as lists per task name
    active = {task.name: [] for task in tasks_list}

    response_times = {task.name: [] for task in tasks_list}
    deadline_misses = {task.name: 0 for task in tasks_list}
    completed_jobs = {task.name: 0 for task in tasks_list}

    for t in range(time_limit):
        # 1) Release new jobs
        for task in tasks_list:
            if t % int(task.T) == 0:
                active[task.name].append({
                    "task": task,                 # reference to task object
                    "release": t,
                    "deadline": t + task.D,        # absolute deadline
                    "remaining": task.C
                })

        # 2) Count deadline misses for unfinished jobs once we pass their deadline
        for task in tasks_list:
            for job in active[task.name]:
                if t >= job["deadline"] and job["remaining"] > 0:
                    deadline_misses[task.name] += 1
                    job["remaining"] = 0  # mark as "done" to avoid recounting

        # 3) Choose the EDF job among ALL active jobs (smallest absolute deadline)
        chosen_job = None
        for task in tasks_list:
            for job in active[task.name]:
                if job["remaining"] > 0:
                    if chosen_job is None or job["deadline"] < chosen_job["deadline"]:
                        chosen_job = job

        # 4) Execute 1 time unit
        if chosen_job is not None:
            chosen_job["remaining"] -= 1

            # Job finishes at the end of this time slot
            if chosen_job["remaining"] <= 0:
                finish = t + 1
                rt = finish - chosen_job["release"]
                task_name = chosen_job["task"].name
                response_times[task_name].append(rt)
                completed_jobs[task_name] += 1

        # 5) Cleanup finished jobs
        for task in tasks_list:
            active[task.name] = [j for j in active[task.name] if j["remaining"] > 0]

    return {
        "response_times": response_times,
        "deadline_misses": deadline_misses,
        "completed_jobs": completed_jobs,
        "time_limit": time_limit
    }