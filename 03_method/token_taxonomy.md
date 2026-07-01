# Token Taxonomy

Working taxonomy for PAET. Token definitions may change, but changes must be logged.

| Token | Meaning | Candidate evidence | Expected decision effect | Status |
|---|---|---|---|---|
| `doorway_narrow` | Doorway or passage has insufficient lateral clearance margin | Map geometry, LiDAR gap, RGB-D depth, robot footprint | Increase risk, prefer detour or slow passage | Draft |
| `human_group_crossing` | Multiple humans are crossing or blocking the robot path | RGB-D people detection, LiDAR tracks, trajectory prediction | Prefer wait or slow passage | Draft |
| `temporary_obstacle` | Current obstacle is absent from the prior map | Occupancy mismatch, RGB-D/LiDAR obstacle cue | Prefer detour or replan | Draft |
| `localization_uncertainty` | Pose estimate is unreliable for current action | Pose covariance, SLAM status, map matching error | Increase risk, avoid narrow/precise maneuvers | Draft |
| `low_clearance` | Vertical or side clearance is below safe margin | Point cloud, depth map, robot envelope | Reject or detour | Draft |
| `high_clearance` | Clearance is sufficient for reliable passage | Point cloud, depth map, robot envelope | Support proceed decision | Draft |
| `wait_required` | Current risk may resolve by waiting | Human flow, temporary obstacle, dynamic blockage | Wait rather than reject | Draft |
| `execution_blocked` | Current task cannot be executed under observed conditions | Combination of tokens and task constraints | Reject or ask for user intervention | Draft |

## Revision Log

| Date | Change | Reason | Approved by |
|---|---|---|---|
| TBD | Initial taxonomy | Project scaffold | TBD |

