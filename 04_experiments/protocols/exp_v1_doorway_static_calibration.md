# Experiment Protocol: Doorway Narrow Static Geometry Calibration

## Experiment ID

EXP-V1-DN-CAL-001

## Purpose

Calibrate and audit the V1 `doorway_narrow` geometric detector before using it
for navigation-task experiments.

This round is stationary. The robot should not drive through the passage during
data collection, and task success rate must not be computed from this protocol.

## Evaluation Scope

This protocol evaluates:

- observed passage-width error;
- event stability during a stationary observation window;
- false positives in negative control areas.

This protocol does not evaluate:

- navigation success;
- collision avoidance;
- completion time;
- recovery behavior;
- human-aware waiting or detour decisions.

## Required Trial Metadata

Each trial must record:

- unique `run_id`;
- manually measured passage width in meters;
- robot pose relative to the passage;
- config file path and threshold/config version;
- event CSV path;
- doorway-gap diagnostic CSV path;
- actual stationary observation-window duration;
- manual label for whether `doorway_narrow` should trigger;
- scenario type: narrow, borderline, wide, open negative, or clutter negative.

Use `04_experiments/templates/doorway_static_calibration_trials.csv` as the trial
manifest schema.

Example `run_id` values:

```text
dncal_20260714_183000_siteA_centered
dncal_20260714_183500_open_negative_A
dncal_20260714_184000_clutter_negative_A
```

## Physical Setup

Robot state:

- Robot remains stationary for the full trial.
- No autonomous navigation goal is sent.
- Emergency stop/supervision remains available.

Sensor/runtime state:

- Start the normal robot stack.
- Start `paet_ros` with a unique `run_id`.
- Prefer the fused scan topic `/scan_ira` unless a sensor fault requires `/scan`.
- Do not store raw images or raw point clouds for this calibration round.

Passage setup:

- Measure the clear physical width at the height and cross-section relevant to
  the 2D scan plane.
- Record the measurement tool and estimated manual measurement uncertainty.
- For each passage, record robot offset and yaw relative to the passage centerline.

Negative controls:

- Open area negative: no nearby side walls, expected no `doorway_narrow`.
- Clutter negative: nearby objects that should not constitute a doorway or
  channel, expected no `doorway_narrow`.

## Minimum Trial Set

Do not begin the full batch immediately after deploying a new tokenizer build.
First run one short smoke trial each in a narrow passage, a wide passage, and an
open area. Confirm that:

- the event and doorway-gap CSV files use the intended unique `run_id`;
- diagnostic rows arrive throughout the stationary observation window;
- valid wide estimates report `width_above_threshold` without an event;
- narrow estimates transition from `min_duration_pending` to `token_triggered`;
- open areas report `no_valid_gap` rather than a fabricated zero-width gap;
- `tools/evaluate_doorway_static_calibration.py` accepts the three-file set.

Only after this smoke gate passes, collect the recommended calibration batch:

| Scenario type | Minimum count | Label |
| --- | ---: | --- |
| Narrow passage | 3 | should trigger |
| Borderline passage | 3 | label from measured threshold rule |
| Wide passage | 3 | should not trigger |
| Open area negative | 3 | should not trigger |
| Clutter negative | 3 | should not trigger |

For each physical location, vary only robot relative placement cautiously:

- centered and approximately perpendicular;
- small lateral offset;
- small yaw offset.

Do not move the robot during a single trial window.

## Run Command

Use a unique `run_id` for every trial:

```bash
RUN_ID=dncal_$(date +%Y%m%d_%H%M%S)_siteA_pos01
roslaunch paet_ros paet_v1.launch run_id:=${RUN_ID}
```

Record the resulting log path:

```text
~/.ros/paet_logs/<run_id>_events.csv
~/.ros/paet_logs/<run_id>_doorway_gap.csv
```

## Trial Duration

Default stationary observation window:

- 10 seconds after PAET startup has subscribed to `/scan_ira`;
- longer windows may be used if scan stability is visibly poor.

Stop PAET with `Ctrl+C` so the logger flushes the active tail segment.

## Threshold Rule for Manual Label

The detector rule under test is:

```text
observed_gap_width - (footprint_width_m + 2 * safety_margin_m) < narrow_margin_threshold_m
```

For manual labels, use the measured physical width:

```text
should_trigger = measured_width_m - (footprint_width_m + 2 * safety_margin_m) < narrow_margin_threshold_m
```

For the current default config:

```text
footprint_width_m = 0.70
safety_margin_m = 0.15
narrow_margin_threshold_m = 0.10
trigger threshold = 1.10 m
```

Borderline trials within manual measurement uncertainty of the threshold should
be flagged as `borderline` and not used for strong accuracy claims.

## Metrics For This Round

Width error:

```text
width_error_m = observed_gap_width_m - measured_width_m
absolute_width_error_m = abs(width_error_m)
```

Use valid `estimated_width_m` rows from the doorway-gap diagnostic CSV. The
summary reports their mean and width-error statistics independently of whether
the token fired. Rows with `estimate_valid=False` describe a missing geometric
estimate; their blank width fields must never be interpreted as zero. Review
the diagnostic `decision` counts to distinguish `no_valid_gap`,
`width_above_threshold`, `min_duration_pending`, and `token_triggered`.

Stability:

- positive stationary trial should normally produce one merged event segment;
- repeated segments within one stationary trial indicate fragmentation;
- absence of an event in a positive trial indicates a miss;
- event duration should cover most of the stationary observation window after
  the detector's `min_event_duration_s`.

The offline summary reports the recorded segment duration divided by the
manifest's `observation_window_s`; interpret this as a diagnostic coverage
ratio, not as navigation success. A ratio above `1.0` indicates that the
recorded event and manually noted observation-window boundaries were misaligned
and should be reviewed rather than silently clipped.

False positives:

- any `doorway_narrow` segment in open-area negative trials is a false positive;
- any `doorway_narrow` segment in clutter negative trials is a false positive.

Do not compute precision, recall, F1, task success rate, or navigation metrics
from this calibration batch unless a separate labeled evaluation protocol is
started.

## Offline Summary

After filling the trial manifest, run:

```bash
python3 tools/evaluate_doorway_static_calibration.py \
  --trials 04_experiments/templates/doorway_static_calibration_trials.csv \
  --output /tmp/doorway_static_calibration_summary.csv
```

The output summary is metadata only. Keep raw logs outside Git and commit only
sanitized aggregate results when appropriate.

## Completion Criteria

- Every trial has a unique `run_id`.
- Every trial has a measured width or a documented negative-control reason.
- Every trial records robot relative placement.
- Every trial points to an event CSV path outside Git.
- Every trial points to a doorway-gap diagnostic CSV path outside Git.
- Negative controls include both open area and clutter area.
- Summary table reports width error, segment count, trigger agreement, and
  false-positive status.
