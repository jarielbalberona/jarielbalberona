from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ledger import DEFAULT_DB, Ledger
from .models import CompanyOrigin, Job
from .monitoring import build_read_only_gmail_plan
from .policy import EmployerExclusionMatcher, evaluate_eligibility
from .runner import DEFAULT_STATE, run_dry_run


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repository-owned job-search control plane")
    subcommands = parser.add_subparsers(dest="command", required=True)

    init = subcommands.add_parser("init", help="initialize ignored private SQLite state")
    init.add_argument("--db", type=Path, default=DEFAULT_DB)

    harden = subcommands.add_parser("harden-ledger", help="normalize legacy private ledger data")
    harden.add_argument("--db", type=Path, default=DEFAULT_DB)

    monitor = subcommands.add_parser("response-monitor-plan", help="emit a read-only Gmail search plan")
    monitor.add_argument("--db", type=Path, default=DEFAULT_DB)

    dry_run = subcommands.add_parser("dry-run", help="persist a normalized DRY_RUN input")
    dry_run.add_argument("--input", type=Path, required=True)
    dry_run.add_argument("--db", type=Path, default=DEFAULT_DB)
    dry_run.add_argument("--state-dir", type=Path, default=DEFAULT_STATE)

    policy = subcommands.add_parser("policy-check", help="privately evaluate employer eligibility")
    policy.add_argument("--company", required=True)
    policy.add_argument("--domain")
    policy.add_argument("--destination-company")
    policy.add_argument("--destination-domain")
    policy.add_argument(
        "--origin", choices=[item.value for item in CompanyOrigin], default=CompanyOrigin.INTERNATIONAL.value
    )

    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "init":
        with Ledger(args.db) as ledger:
            ledger.initialize()
        print(json.dumps({"initialized": True, "db": str(args.db)}))
        return 0

    if args.command == "dry-run":
        print(json.dumps(run_dry_run(args.input, db_path=args.db, state_dir=args.state_dir), indent=2))
        return 0

    if args.command == "harden-ledger":
        with Ledger(args.db) as ledger:
            ledger.initialize()
            result = ledger.harden_existing_data()
        print(json.dumps({"db": str(args.db), **result}, sort_keys=True))
        return 0

    if args.command == "response-monitor-plan":
        with Ledger(args.db) as ledger:
            ledger.initialize()
            rows = ledger.connection.execute(
                """
                SELECT a.application_id, a.status, j.company, j.role
                FROM applications a JOIN jobs j ON j.job_id = a.job_id
                ORDER BY a.updated_at DESC
                """
            ).fetchall()
            plan = build_read_only_gmail_plan(dict(row) for row in rows)
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0

    if args.command == "policy-check":
        job = Job(
            source="private-policy-check",
            role="Senior Software Engineer",
            company=args.company,
            description="Hands-on senior product engineering role.",
            original_url="https://example.invalid/job",
            company_origin=CompanyOrigin(args.origin),
            company_domain=args.domain,
            destination_company=args.destination_company,
            destination_domain=args.destination_domain,
            remote_from_ph=True,
            engineering_domain_eligible=True,
        )
        result = evaluate_eligibility(job, EmployerExclusionMatcher.load())
        print(
            json.dumps(
                {
                    "can_score": result.can_score,
                    "verdict": result.verdict.value if result.verdict else None,
                    "reason_codes": result.reason_codes,
                }
            )
        )
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
