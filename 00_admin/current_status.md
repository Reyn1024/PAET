# Current Status

## Infrastructure

- Workspace scaffold: created.
- Git: installed and configured; repository is synchronized with `Reyn1024/PAET` on branch `main`.
- Robot-side workflow: source changes and sanitized validation facts are synchronized through GitHub.
- ROS package: `ros/paet_ros` builds in the robot's ROS 1 Noetic catkin workspace.
- Zotero/BibTeX integration: planned.

## Research Stage

- Manuscript type: PAET method paper.
- Research maturity: PAET V1 geometry-first method and two minimum experiment protocols are defined; accuracy evaluation has not started.
- Experiment route: ROS/Gazebo simulation plus limited real-robot cases.
- Real robot platform: ROS 1 Noetic building robot; available topics and system facts are recorded under `04_experiments/`.

## Latest Validation

- Validation date: 2026-07-14.
- Validated revision: `6477bf9`.
- `paet_ros` passed `catkin_make` and launched with the robot navigation stack.
- `/paet/events` and `/paet/debug_markers` were published with the expected message types.
- One live `doorway_narrow` event and corresponding marker were observed.
- This is integration evidence only. It does not establish precision, recall, F1, or detector validity.
- The observed clearance margin was `-0.004 m`, so the sample is especially sensitive to scan noise, footprint calibration, and threshold choice.
- Commit `9a37b2b` added scan-rate event merging: one CSV/JSONL row now represents one event segment, with a default `0.75 s` gap threshold.
- Commit `7dee88b` added unique launch-time `run_id` values and a synthetic ROS validation helper.
- Robot-side logger validation passed continuous merging, sub-gap merging, over-gap splitting, shutdown flush, unique `run_id`, and catkin build checks.
- These checks validate logging semantics only; they do not provide token-detection performance evidence.
- The scan-rate doorway-gap diagnostic stream and CSV logger passed robot-side synthetic validation at revision `31c9489`, including all four decisions and wrong-`run_id` rejection.
- The three-case stationary smoke gate passed for a 0.95 m narrow doorway, 2.70 m wide doorway, and open-area negative control; no false positives, misses, or fragmented events occurred in the accepted trials.
- The narrow estimate was 0.861 m and a preliminary non-compliant setup missed the same doorway, confirming substantial placement and door-state sensitivity; this is smoke evidence, not detector accuracy.

## Immediate Next Actions

1. Freeze the 15-run condition list and the protocol's inclusion/exclusion rules before further collection.
2. Run three trials each for narrow, borderline, wide, open-area negative, and clutter negative scenarios.
3. Retain every initiated run; document technical exclusions and repeat them under a new `run_id`, but never exclude an unexpected detector result.
4. Record manual width, robot placement, config version, event and diagnostic paths, and manual label for every analyzed trial.
5. Review placement sensitivity and width error before freezing thresholds or starting navigation-task experiments.

## Feasibility Review

- Robot platform facts have been synchronized from GitHub.
- PAET V1 feasibility has been assessed in `04_experiments/paet_feasibility_assessment.md`.
- Current recommendation: proceed with a scoped V1 focused on LiDAR/map/localization-driven physical traversal tokens; defer robust human-group and language-conditioned waiting tokens to Phase 2.
