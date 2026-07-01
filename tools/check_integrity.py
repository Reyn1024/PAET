import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    issues = []

    literature = read_csv(ROOT / "02_literature" / "literature_registry.csv")
    claims = read_csv(ROOT / "02_literature" / "claims_ledger.csv")
    experiments = read_csv(ROOT / "04_experiments" / "experiment_registry.csv")
    results = read_csv(ROOT / "05_results" / "result_registry.csv")
    figures = read_csv(ROOT / "07_figures_tables" / "figure_registry.csv")
    tables = read_csv(ROOT / "07_figures_tables" / "table_registry.csv")

    verified_refs = {
        row.get("citation_key", "").strip()
        for row in literature
        if row.get("verification_status", "").strip().lower() == "verified"
    }
    experiment_ids = {
        row.get("experiment_id", "").strip()
        for row in experiments
        if row.get("experiment_id", "").strip()
    }
    result_experiment_ids = {
        row.get("experiment_id", "").strip()
        for row in results
        if row.get("experiment_id", "").strip()
    }

    for row in claims:
        claim_id = row.get("claim_id", "").strip() or "<missing claim_id>"
        allowed = row.get("allowed_in_manuscript", "").strip().lower() == "yes"
        evidence_type = row.get("evidence_type", "").strip().lower()
        citation_key = row.get("citation_key", "").strip()
        experiment_id = row.get("experiment_id", "").strip()
        status = row.get("verification_status", "").strip().lower()

        if allowed and status != "verified":
            issues.append(f"Claim {claim_id} is allowed in manuscript but not verified.")
        if allowed and evidence_type == "paper" and citation_key not in verified_refs:
            issues.append(f"Claim {claim_id} cites unverified or missing source: {citation_key}.")
        if allowed and evidence_type == "experiment" and experiment_id not in experiment_ids:
            issues.append(f"Claim {claim_id} references missing experiment: {experiment_id}.")

    for row in results:
        result_id = row.get("result_id", "").strip() or "<missing result_id>"
        experiment_id = row.get("experiment_id", "").strip()
        allowed = row.get("allowed_in_manuscript", "").strip().lower() == "yes"
        status = row.get("verification_status", "").strip().lower()
        if experiment_id and experiment_id not in experiment_ids:
            issues.append(f"Result {result_id} references missing experiment: {experiment_id}.")
        if allowed and status != "verified":
            issues.append(f"Result {result_id} is allowed in manuscript but not verified.")

    for registry_name, rows in [("figure", figures), ("table", tables)]:
        for row in rows:
            item_id = row.get(f"{registry_name}_id", "").strip() or f"<missing {registry_name}_id>"
            allowed = row.get("allowed_in_manuscript", "").strip().lower() == "yes"
            status = row.get("verification_status", "").strip().lower()
            experiment_id = row.get("experiment_id", "").strip()
            if allowed and status != "verified":
                issues.append(f"{registry_name.title()} {item_id} is allowed in manuscript but not verified.")
            if experiment_id and experiment_id not in experiment_ids and experiment_id not in result_experiment_ids:
                issues.append(f"{registry_name.title()} {item_id} references missing experiment: {experiment_id}.")

    if issues:
        print("Integrity check failed:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)

    print("Integrity check passed: no registry inconsistencies detected.")


if __name__ == "__main__":
    main()

