# Manuscript Outline

## Title

Physical-Affordance Event Tokenization for Building-Scale Robot Navigation

## Intended Storyline

Building robots need more than semantic maps or shortest paths. They need an intermediate representation that captures physical execution meaning: whether a route is narrow, blocked by temporary obstacles, affected by human crossing, or unreliable due to localization uncertainty. PAET provides this event layer and supports risk, wait, detour, and failure-reason decisions.

## Section Goals

| Section | Goal | Evidence required |
|---|---|---|
| Introduction | Establish the gap between map traversability and physical executability | Verified literature |
| Related Work | Compare affordance learning, traversability, semantic maps, social navigation, risk-aware navigation, VLA | Verified literature |
| Problem Formulation | Define inputs, outputs, and decision context | Method definition |
| Method | Define PAET architecture and token schema | Method definition |
| Experiments | Define simulation and real-robot evaluation | Experiment protocols |
| Results | Report only completed and verified results | Experiment registry |
| Discussion | Interpret strengths, failures, and boundary conditions | Results and literature |
| Limitations | State constraints honestly | Project records |

## Claim Control

Before adding a substantive claim to `main.md`, add it to `02_literature/claims_ledger.csv`.

