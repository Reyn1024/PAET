# Research Question Brief

## Working Research Question

How can a building-service robot convert multimodal observations into physical-affordance event tokens that explicitly represent traversal risk, waiting needs, and execution-failure causes?

## Candidate Sub-Questions

1. Which event-token taxonomy best captures building-scale navigation risks such as narrow doorways, dynamic human crossings, temporary obstacles, clearance constraints, and localization uncertainty?
2. How can RGB-D, LiDAR, semantic maps, odometry/localization signals, and task instructions be fused to detect these event tokens?
3. Do PAET tokens improve navigation decision quality compared with costmap-only, traversability-only, or semantic-map-only baselines?
4. Can PAET tokens support faithful explanations of wait, detour, reject, or proceed decisions?

## Candidate Contributions

- A physical-affordance event-token taxonomy for building-scale robot navigation.
- A multimodal tokenizer architecture for detecting event tokens.
- A traceable link from event tokens to traversal risk, waiting decisions, and failure-reason diagnosis.
- A ROS/Gazebo evaluation protocol plus limited real-robot case validation.

## Boundaries

The first manuscript should not claim a complete building-scale world model unless the memory and planning components are fully implemented and evaluated.

