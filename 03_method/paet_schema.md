# PAET Schema

This file defines the working input/output schema for the Physical-Affordance Event Tokenizer.

## Inputs

| Channel | Example data | Purpose | Status |
|---|---|---|---|
| RGB-D | color image, depth image | object, people, clearance, obstacle cues | Planned |
| LiDAR | scan or point cloud | geometry, free space, dynamic obstacles | Planned |
| Semantic map | rooms, doors, corridors, landmarks | semantic context | Planned |
| Localization | pose, covariance, odometry, SLAM quality | uncertainty and map alignment | Planned |
| Task instruction | natural language or task label | task-conditioned risk relevance | Planned |

## Output Event Record

```json
{
  "token": "doorway_narrow",
  "confidence": 0.0,
  "spatial_anchor": {
    "frame": "map",
    "x": null,
    "y": null,
    "z": null
  },
  "time_window": {
    "start": null,
    "end": null
  },
  "evidence_channels": [],
  "suggested_effect": {
    "risk_delta": null,
    "wait_recommended": null,
    "detour_recommended": null,
    "reject_recommended": null
  },
  "notes": "TBD"
}
```

Do not fill numeric values until implementation and experiments provide evidence.

