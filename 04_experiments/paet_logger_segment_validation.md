# PAET Logger Segment Validation

Date: 2026-07-14

Repository base before fix: `47f6add Track PAET event segment logger validation`

## Issue

`paet_v1.launch` did not expose `run_id`, so the logger fell back to the fixed
configuration value `paet_v1_dry_run`. Because the logger opens CSV/JSONL files
in append mode, multiple trials could write into the same files and mix trial
records.

The logger also needs to emit merged event segments for evaluation rather than
scan-rate duplicate rows.

## Fix

- Added `run_id` as a `paet_v1.launch` argument.
- Passed `run_id` into `paet_event_logger.py` as a private parameter.
- Kept the launch default unique by using `$(anon paet_v1)`.
- Added `paet_logger_segment_validation.py`, a synthetic ROS validation helper
  for repeatable logger segment tests.
- Documented unique `run_id` usage in `ros/paet_ros/README.md`.

## Validation Command

Run from the robot workspace with ROS master available:

```bash
source ~/.bashrc
source /home/robot/catkin_ws/devel/setup.bash
rosrun paet_ros paet_logger_segment_validation.py
```

Observed result:

```text
continuous_updates_one_row ok: rows=1 run_id=continuous_updates_one_row_e70eb8c2
short_gap_one_row ok: rows=1 run_id=short_gap_one_row_8c44362c
long_gap_two_rows ok: rows=2 run_id=long_gap_two_rows_0f66b7d5
ctrl_c_flushes_tail ok: rows=1 run_id=ctrl_c_flushes_tail_28b521c9
```

## Acceptance Checks

| Check | Result |
| --- | --- |
| Continuous updates produce 1 row | Pass |
| Interruption shorter than 0.75 s remains 1 row | Pass |
| Interruption longer than 0.75 s produces 2 rows | Pass |
| Ctrl+C flushes the active tail segment | Pass |
| Each trial uses a unique run_id | Pass |

## Build Check

`catkin_make` passed after installing the new validation helper:

- `paet_logger_segment_validation.py` devel wrapper installed under
  `/home/robot/catkin_ws/devel/lib/paet_ros`.

## Launch Parameter Check

Command:

```bash
roslaunch --dump-params paet_ros paet_v1.launch run_id:=trial_test
```

Relevant output:

```text
/logging/run_id: paet_v1_dry_run
/paet_event_logger/run_id: trial_test
```

This confirms the logger uses the launch-provided private `run_id`, so a trial
can avoid appending into the default `paet_v1_dry_run` log files.
