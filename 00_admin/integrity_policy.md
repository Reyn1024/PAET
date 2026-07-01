# Integrity Policy

## Non-Fabrication Rules

Never invent:

- references,
- DOIs,
- page numbers,
- quotations,
- datasets,
- robot platforms,
- experimental settings,
- numerical results,
- statistical significance,
- reviewer comments.

If information is unknown, write `TBD`, `unverified`, or `planned`, not a plausible-looking substitute.

## Literature Rules

A source is manuscript-citable only when all are true:

- It is listed in `02_literature/literature_registry.csv`.
- `verification_status` is `verified`.
- `source_access` points to a PDF, DOI landing page, official publisher page, arXiv page, or stable project page.
- The claim being cited is recorded in `02_literature/claims_ledger.csv`.

Unverified sources may be kept in notes, but manuscript prose must label them as unverified and must not cite them as evidence.

## Claim Rules

Every substantive manuscript claim must be registered in `02_literature/claims_ledger.csv`.

Allowed evidence types:

- `paper`: verified paper or report.
- `experiment`: registered simulation or real-robot experiment.
- `method_definition`: a definition introduced by this project.
- `assumption`: explicitly labeled assumption, not a result.

Claims about performance require `experiment` evidence.

## Experiment Rules

Every experimental result must map to one row in `04_experiments/experiment_registry.csv`.

Each experiment record must include:

- protocol path,
- environment,
- data path,
- configuration path,
- random seed or `not_applicable`,
- script or commit/snapshot reference,
- result path,
- reproducibility status.

Do not write results in the manuscript before the experiment status is `completed` or `audited`.

## Privacy and Human-Subject Safety

Real-robot building data may contain faces, body trajectories, voices, badges, room identifiers, or other personal information.

Default policy:

- Treat real building data as privacy-sensitive.
- Do not publish identifiable images or trajectories.
- Store raw sensitive data outside Git.
- Use anonymized figures and aggregated metrics.
- Document ethics/privacy handling in `04_experiments/privacy_ethics.md`.

## Deletion and Archival Rules

Default action for obsolete files is archive, not delete.

Use `archive/README.md` to document:

- original path,
- archive date,
- reason,
- replacement file if any.

