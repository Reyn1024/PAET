# Project Charter

## Project Identity

- Working title: Physical-Affordance Event Tokenization for Building-Scale Robot Navigation
- Short name: PAET
- Manuscript type: Method paper
- Target outlet: Generic SCI manuscript first; journal-specific formatting later
- Working language: English manuscript, Chinese or English research notes
- Maintainers: User + Codex

## Research Goal

Develop and evaluate a Physical-Affordance Event Tokenizer that converts multimodal robot observations into physically meaningful event tokens for building-scale navigation.

Core question:

> How can RGB-D, LiDAR, semantic maps, odometry/localization signals, and task instructions be converted into physical-affordance event tokens that describe traversal risk, waiting needs, and likely execution-failure causes?

## Initial Scope

In scope:

- PAET token taxonomy.
- Tokenizer input/output schema.
- Risk, waiting, and failure-reason modeling.
- ROS/Gazebo simulation experiments.
- Limited real-robot building cases.
- Literature review with source verification.
- Generic SCI manuscript.

Out of scope for the first manuscript unless resources allow:

- Full dynamic semantic topological memory as the main contribution.
- Full counterfactual explanation system as the main contribution.
- Large-scale deployment across many buildings.
- Claims about superior performance without completed experiments.

## Weekly Iteration Rule

Each week should produce at least one inspectable artifact:

- verified literature entry,
- claim ledger update,
- method subsection,
- experiment protocol,
- experiment run record,
- figure/table draft,
- manuscript section,
- review or submission artifact.

Update `00_admin/weekly_review.md` at the end of each week.

## File Safety Rule

Do not delete project files by default. Move outdated files to `archive/` with a note explaining why they were archived, or ask the user for approval before deletion.

