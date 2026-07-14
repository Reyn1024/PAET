# PAET SCI Manuscript Project

This repository is a long-running writing and research workspace for a SCI manuscript on Physical-Affordance Event Tokenization (PAET).

Primary goal:

- Develop a PAET method paper from research-question refinement through literature verification, method design, ROS/Gazebo experiments, limited real-robot validation, manuscript drafting, and submission preparation.

Non-negotiable rules:

- Do not fabricate references, page numbers, data, or experimental results.
- Do not delete project files without explicit user approval.
- Every manuscript claim must trace to a verified source, an experiment record, or a clearly marked assumption.
- Unverified papers may support notes, but not manuscript citations.
- Unfinished experiments may appear only as planned protocols, not as results.

Start here:

1. Read `00_admin/project_charter.md`.
2. Read `00_admin/integrity_policy.md`.
3. Update `01_research_question/research_question_brief.md`.
4. Add verified papers to `02_literature/literature_registry.csv`.
5. Register manuscript claims in `02_literature/claims_ledger.csv`.
6. Register experiments in `04_experiments/experiment_registry.csv`.
7. Draft the English manuscript in `06_manuscript/main.md`.

Current infrastructure note:

- Git and GitHub synchronization are active on branch `main`.
- The ROS 1 Noetic package under `ros/paet_ros` has passed robot-side build and runtime integration validation.
- See `00_admin/current_status.md` for the current research stage and next actions.
