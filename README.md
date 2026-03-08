# realtime-wcrt-tool
# Realtime WCRT Tool

Realtime Scheduling Analysis Tool

This project was developed for the course 02225 Distributed Real-Time Systems (DRTS) – Mini-project 1.
The program analyzes schedulability and response times of periodic real-time task sets running on a single processor.

The implementation includes:

Deadline Monotonic (DM) schedulability analysis using Response Time Analysis (RTA)

Earliest Deadline First (EDF) schedulability analysis using the Processor Demand Approach (PDA)

A discrete-time simulation of both DM and EDF scheduling

Export of results to CSV files for later analysis

The program can be used with both simple custom task sets and the task sets provided in the course repository.

Project structure

src/
main.py
task.py
csv_loader.py
dm_rta.py
edf_pda.py
simulator.py

tasks/
example task sets and course task sets

results/
run_results_dm.csv
run_results_edf.csv

How to run the program?

Run the program from the project root folder.

Default example:

python src/main.py

This runs the program on a small example task set.

Run with a specific task set

python src/main.py "<path_to_csv>" 200000

Example:

python src/main.py "tasks\course_tasksets\output\unifast-utilDist\uniform-discrete-perDist\1-core\25-task\0-jitter\0.10-util\tasksets\uniform-discrete_0.csv" 200000

The second argument is the simulation time limit.

Output

The program prints:

DM analytical response times (RTA)

EDF schedulability result (PDA)

DM simulation results

EDF simulation results

Results are also saved to:

results/run_results_dm.csv
results/run_results_edf.csv

Running multiple task sets

Multiple task sets can be tested automatically using a PowerShell loop:

$base = "tasks\course_tasksets\output\unifast-utilDist\uniform-discrete-perDist\1-core\25-task\0-jitter"
$utils = @("0.10","0.30","0.50","0.70","0.80","0.90")
$timeLimit = 200000
$perUtilSets = 5

foreach ($u in $utils) {
for ($i=0; $i -lt $perUtilSets; $i++) {
$file = "$base$u-util\tasksets\uniform-discrete_$i.csv"
if (Test-Path $file) {
python src/main.py "$file" $timeLimit
}
}
}

This runs several task sets with different utilization levels.

Requirements

Python 3
No external libraries are required.

Project goal

The goal of the project is to compare DM and EDF scheduling by:

computing analytical worst-case response times

verifying behavior through simulation

evaluating schedulability at different utilization levels.