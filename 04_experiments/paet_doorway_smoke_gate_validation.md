# PAET Doorway Diagnostic Smoke Gate Validation

## Scope

- Date: 2026-07-14
- Code revision: `31c9489`
- Platform: current ROS 1 Noetic building robot
- Mode: stationary, no navigation goal, no PAET motion command
- Input: fused 2D scan `/scan_ira`
- Configuration: `ros/paet_ros/config/paet_v1.yaml`

This validation checked the doorway-gap diagnostic and logging path before the
full 15-trial static calibration. It is a smoke gate, not a detector-accuracy
evaluation.

## Synthetic ROS Validation

The robot-side command was:

```bash
rosrun paet_ros paet_doorway_gap_validation.py
```

Observed acceptance output:

```text
doorway-gap diagnostic logging ok: rows=4 rejected_wrong_run_id=1
```

The four diagnostic decisions were covered:

- `no_valid_gap`;
- `width_above_threshold`;
- `min_duration_pending`;
- `token_triggered`.

A deliberately incorrect `run_id` was rejected by the logger and was not
written to the diagnostic CSV.

## Stationary Smoke Trials

Each accepted trial recorded approximately 10 seconds after diagnostic rows
started arriving. Doors remained open and fixed during doorway trials.

| Scenario | Manual width | Diagnostic samples | Valid estimates | Mean estimate | Estimate range | Event result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Narrow doorway | 0.950 m | 202 | 202 | 0.861 m | 0.852-0.882 m | One `doorway_narrow` segment |
| Wide doorway | 2.700 m | 203 | 202 | 2.675 m | 2.668-2.680 m | No event |
| Open-area negative | not applicable | 202 | 0 | unavailable | unavailable | No event |

Narrow-door diagnostics contained 9 `min_duration_pending` samples followed by
193 `token_triggered` samples. The mean width error was `-0.089 m`.

Wide-door diagnostics contained one startup `no_valid_gap` sample followed by
202 `width_above_threshold` samples. The mean width error was `-0.025 m`.

All 202 open-area samples were `no_valid_gap`. Invalid estimates retained blank
geometry fields and were not interpreted as zero-width gaps.

## Offline Summary

The three accepted trial manifests were evaluated together with:

```bash
python3 tools/evaluate_doorway_static_calibration.py \
  --trials <external-smoke-manifest.csv> \
  --output <external-smoke-summary.csv>
```

Combined result:

```text
trials,3
false_positives,0
missed_positives,0
fragmented_static_events,0
```

The narrow event coverage ratio was `1.005`, reflecting an approximately
`0.05 s` difference between the first diagnostic timestamp and the event
segment boundary. It was retained for review rather than clipped.

## Setup Sensitivity Observation

Before the accepted narrow trial, a preliminary setup check produced a mean
estimate of `1.390 m` for the same manually measured `0.950 m` doorway and did
not trigger. That check occurred before the open, fixed-door setup was
confirmed and was excluded from the smoke gate. It demonstrates that the
current nearest-left/right rule is sensitive to door state, robot standoff,
lateral offset, and yaw. The full calibration must preserve these placement
variables rather than treating the accepted smoke result as accuracy evidence.

## Data Handling

- Raw event CSV, event JSONL, and scan-rate diagnostic CSV files remain outside Git.
- No raw scan, image, network, credential, or precise site-location data is committed.
- This report contains sanitized aggregate metadata only.

## Decision

The diagnostic and logging smoke gate passed. The full 15-trial stationary
calibration may proceed with three trials each for narrow, borderline, wide,
open-area negative, and clutter negative scenarios. Detector thresholds must
not be frozen until the placement-sensitive width error is reviewed.
