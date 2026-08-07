"""Gavaza command-line interface (argparse, standard library only)."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from gavaza import __version__
from gavaza.assess import (
    Assessment,
    load_results,
    run_interactive,
    save_results,
)
from gavaza.breach import (
    BreachRecord,
    add_breach,
    list_breaches,
    notification_checklist,
    notification_timeline,
    parse_affected,
)
from gavaza.config import Company, docs_dir, load_config, save_config
from gavaza.generate import write_docs
from gavaza.requests import REQUEST_RIGHTS, REQUEST_STATUSES
from gavaza.report import latest_results_path, render, summary_lines

DOC_CHOICES = ("paia", "privacy", "register", "operator", "dsr-form", "consent", "retention", "pia")
FORMAT_CHOICES = ("json", "md", "html")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gavaza",
        description=(
            "Gavaza — POPIA compliance toolkit. Model the eight POPIA conditions, "
            "assess compliance, and generate PAIA manuals, privacy policies, "
            "processing registers and breach registers."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"gavaza {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # gavaza init
    init = sub.add_parser(
        "init", help="create the company configuration and output directory"
    )
    init.add_argument("company_json", nargs="?", help="path to an existing company.json")
    init.add_argument("--name", help="company name")
    init.add_argument("--reg", help="registration number")
    init.add_argument("--address", help="registered address")
    init.add_argument("--email", help="contact email")
    init.add_argument("--info-officer", help="Information Officer name")
    init.add_argument("--contact", help="contact telephone or other details")

    # gavaza assess
    assess = sub.add_parser(
        "assess", help="run the POPIA compliance questionnaire"
    )
    assess.add_argument(
        "--interactive", action="store_true", help="prompt for every question"
    )
    assess.add_argument(
        "--answers", help="JSON file of scripted answers ({item_id: 'yes'|'no'|'partial'})"
    )
    assess.add_argument("--out", help="path for the results JSON (default: <data-dir>/assessment.json)")

    # gavaza report
    report = sub.add_parser("report", help="render the assessment report")
    report.add_argument(
        "--format", choices=FORMAT_CHOICES, default="md", help="report format (default: md)"
    )
    report.add_argument("--out", help="output file path")
    report.add_argument("--results", help="assessment results JSON to read (default: latest)")

    # gavaza generate
    generate = sub.add_parser("generate", help="generate compliance documents")
    generate.add_argument(
        "--docs",
        nargs="+",
        choices=[*DOC_CHOICES, "all"],
        default=["all"],
        help="documents to generate (default: all)",
    )
    generate.add_argument("--out", help="output directory (default: <data-dir>/docs)")

    # gavaza breach
    breach = sub.add_parser("breach", help="manage the breach register")
    breach_sub = breach.add_subparsers(dest="breach_command", required=True)
    add = breach_sub.add_parser("add", help="log a breach and print the 72-hour checklist")
    add.add_argument("--date", help="date of the breach (ISO format, default: today)")
    add.add_argument("--description", required=True, help="what happened")
    add.add_argument("--categories", help="categories of personal information involved")
    add.add_argument(
        "--affected", type=parse_affected, default=0, help="number of affected data subjects"
    )
    add.add_argument("--risk", help="risk assessment (e.g. low/medium/high with rationale)")
    add.add_argument("--status", default="not notified", help="notification status")
    breach_sub.add_parser("list", help="list logged breaches")
    breach_sub.add_parser("timeline", help="print the breach notification timeline guide")

    # gavaza conditions
    sub.add_parser("conditions", help="list the eight POPIA conditions and their checklists")

    # gavaza evidence
    evidence = sub.add_parser("evidence", help="manage evidence for checklist items")
    evidence_sub = evidence.add_subparsers(dest="evidence_command", required=True)
    ev_add = evidence_sub.add_parser("add", help="attach a file to a checklist item")
    ev_add.add_argument("item_id", help="checklist item id (e.g. acc-1)")
    ev_add.add_argument("file", help="path of the evidence file")
    ev_add.add_argument("--note", default="", help="optional note")
    ev_list = evidence_sub.add_parser("list", help="list recorded evidence")
    ev_list.add_argument("--item", help="filter by item id")
    ev_remove = evidence_sub.add_parser("remove", help="remove an evidence entry")
    ev_remove.add_argument("id", help="evidence entry id (e.g. ev-1)")

    # gavaza sections
    sections = sub.add_parser(
        "sections", help="list the additional POPIA compliance sections"
    )
    sections.add_argument(
        "--slug", help="print only the section with this slug"
    )

    # gavaza gdpr-map
    gdpr_map = sub.add_parser(
        "gdpr-map", help="print the POPIA to GDPR mapping"
    )
    gdpr_map.add_argument(
        "--format", choices=("md", "json"), default="md", help="output format (default: md)"
    )

    # gavaza requests
    requests = sub.add_parser("requests", help="manage data subject requests")
    requests_sub = requests.add_subparsers(dest="requests_command", required=True)
    req_new = requests_sub.add_parser("new", help="log a data subject request")
    req_new.add_argument("--name", required=True, help="requester name")
    req_new.add_argument("--email", required=True, help="requester email")
    req_new.add_argument(
        "--right",
        required=True,
        choices=list(REQUEST_RIGHTS),
        help="right being exercised",
    )
    req_new.add_argument("--description", required=True, help="what the request asks for")
    req_new.add_argument("--notes", default="", help="optional notes")
    req_list = requests_sub.add_parser("list", help="list data subject requests")
    req_list.add_argument("--status", choices=list(REQUEST_STATUSES), help="filter by status")
    req_status = requests_sub.add_parser("status", help="update a request status")
    req_status.add_argument("id", help="request id (e.g. req-1)")
    req_status.add_argument("new_status", choices=list(REQUEST_STATUSES), help="new status")
    requests_sub.add_parser("overdue", help="list requests past their deadline")

    return parser


def _cmd_init(args: argparse.Namespace) -> int:
    source = Path(args.company_json) if args.company_json else None
    if source and source.exists():
        with source.open("r", encoding="utf-8") as handle:
            company = Company.from_dict(json.load(handle))
    else:
        if not args.name:
            print(
                "error: provide a company.json file or --name (with optional "
                "--reg, --address, --email, --info-officer, --contact)",
                file=sys.stderr,
            )
            return 2
        company = Company(
            name=args.name,
            reg_no=args.reg or "",
            address=args.address or "",
            email=args.email or "",
            info_officer=args.info_officer or "",
            contact=args.contact or "",
        )
    saved = save_config(company)
    out = docs_dir()
    print(f"Company configuration written to {saved}")
    print(f"Output directory ready: {out}")
    return 0


def _cmd_assess(args: argparse.Namespace) -> int:
    try:
        company = load_config()
    except FileNotFoundError:
        print(
            "error: no company configuration found — run 'gavaza init' first",
            file=sys.stderr,
        )
        return 1
    if args.answers:
        answers_path = Path(args.answers)
        with answers_path.open("r", encoding="utf-8") as handle:
            raw_answers = json.load(handle)
        assessment = Assessment(company)
        for item_id, raw in raw_answers.items():
            try:
                assessment.answer(item_id, raw)
            except KeyError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 1
    elif args.interactive:
        assessment = run_interactive(company)
    else:
        # Non-interactive baseline: everything unanswered scores zero.
        assessment = Assessment(company)
        print(
            "note: no --answers or --interactive given; running with all items "
            "unanswered (scores as 'no').",
            file=sys.stderr,
        )
    out = Path(args.out) if args.out else latest_results_path(None)
    save_results(assessment, out)
    print(f"Results saved to {out}")
    for line in summary_lines(assessment):
        print(line)
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    try:
        company = load_config()
    except FileNotFoundError:
        company = None
    results_path = Path(args.results) if args.results else latest_results_path(None)
    if not results_path.exists():
        print(
            f"error: no assessment results at {results_path} — run 'gavaza assess' first",
            file=sys.stderr,
        )
        return 1
    assessment = load_results(results_path, company=company)
    content = render(assessment, args.format)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        print(f"Report written to {out}")
    else:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    try:
        company = load_config()
    except FileNotFoundError:
        print(
            "error: no company configuration found — run 'gavaza init' first",
            file=sys.stderr,
        )
        return 1
    docs = list(DOC_CHOICES) if "all" in args.docs else args.docs
    out = Path(args.out) if args.out else docs_dir()
    written = write_docs(company, docs=docs, out_dir=out)
    for doc, path in written.items():
        print(f"Generated {doc}: {path}")
    return 0


def _cmd_breach(args: argparse.Namespace) -> int:
    if args.breach_command == "add":
        record = BreachRecord(
            date=args.date or BreachRecord().date,
            description=args.description,
            categories=args.categories or "",
            affected_count=args.affected,
            risk_assessment=args.risk or "",
            notification_status=args.status,
        )
        path = add_breach(record)
        print(f"Breach logged in {path}")
        print()
        print("72-hour notification checklist (POPIA section 22):")
        for index, step in enumerate(notification_checklist(), 1):
            print(f"  {index}. {step}")
        return 0
    if args.breach_command == "list":
        records = list_breaches()
        if not records:
            print("No breaches logged yet.")
            return 0
        for record in records:
            print(
                f"{record.date} | affected: {record.affected_count} | "
                f"{record.description} | status: {record.notification_status}"
            )
        return 0
    # timeline
    for step in notification_timeline():
        print(f"[{step['when']}] {step['action']}")
    return 0


def _cmd_evidence(args: argparse.Namespace) -> int:
    """Manage evidence attached to checklist items."""
    from gavaza.evidence import add_evidence, list_evidence, remove_evidence

    if args.evidence_command == "add":
        entry = add_evidence(args.item_id, args.file, note=args.note)
        print(
            f"Evidence added: {entry.id} -> {entry.item_id} ({entry.file}, "
            f"sha256 {entry.sha256[:12]}...)"
        )
        return 0
    if args.evidence_command == "list":
        entries = list_evidence(item_id=args.item)
        if not entries:
            print("No evidence recorded.")
            return 0
        for entry in entries:
            print(f"{entry.id} | {entry.item_id} | {entry.file} | {entry.date}"
                  + (f" | {entry.note}" if entry.note else ""))
        return 0
    # remove
    if remove_evidence(args.id):
        print(f"Removed evidence {args.id}.")
    else:
        print(f"error: no evidence with id {args.id!r}", file=sys.stderr)
        return 1
    return 0


def _cmd_conditions() -> int:
    from gavaza.conditions import CONDITIONS

    for index, condition in enumerate(CONDITIONS, 1):
        print(f"{index}. {condition.name} ({condition.act_reference}) — {condition.slug}")
        print(f"   {condition.description}")
        for item in condition.checklist:
            print(f"   - [{item.id}] {item.question}")
        print()
    return 0


def _cmd_requests(args: argparse.Namespace) -> int:
    """Manage data subject requests."""
    from gavaza.requests import (
        list_requests,
        new_request,
        overdue_requests,
        update_status,
    )

    if args.requests_command == "new":
        request = new_request(
            args.name, args.email, args.right, args.description, notes=args.notes
        )
        print(
            f"{request.id} | {request.requester_name} | {request.right} | "
            f"received {request.received_at} | deadline {request.deadline}"
        )
        return 0
    if args.requests_command == "list":
        entries = list_requests(status=args.status)
        if not entries:
            print("No data subject requests.")
            return 0
        for request in entries:
            flag = " OVERDUE" if request.overdue else ""
            print(
                f"{request.id} | {request.requester_name} | {request.right} | "
                f"{request.status} | deadline {request.deadline}{flag}"
            )
        return 0
    if args.requests_command == "status":
        if update_status(args.id, args.new_status):
            print(f"{args.id} status set to {args.new_status}.")
        else:
            print(f"error: no request with id {args.id!r}", file=sys.stderr)
            return 1
        return 0
    # overdue
    overdue = overdue_requests()
    if not overdue:
        print("No overdue requests.")
        return 0
    for request in overdue:
        print(
            f"{request.id} | {request.requester_name} | {request.right} | "
            f"deadline {request.deadline}"
        )
    return 0


def _cmd_gdpr_map(args: argparse.Namespace) -> int:
    """Print the POPIA to GDPR mapping."""
    from gavaza.gdpr import render_json, render_markdown

    content = render_json() if args.format == "json" else render_markdown()
    sys.stdout.write(content)
    if not content.endswith("\n"):
        sys.stdout.write("\n")
    return 0


def _cmd_sections(args: argparse.Namespace) -> int:
    """List the additional POPIA compliance sections."""
    from gavaza.sections import SECTION_MAP

    if args.slug:
        section = SECTION_MAP[args.slug]
        _print_section(section)
        return 0
    for section in SECTION_MAP.values():
        _print_section(section)
        print()
    return 0


def _print_section(section) -> None:
    """Print one section with its items."""
    print(f"{section.name} ({section.slug})  [{section.act_reference}]")
    print(f"  {section.description}")
    for item in section.items:
        print(f"  - {item.id}: {item.requirement}")
        print(f"      Guidance: {item.guidance}")


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point: parse arguments, dispatch, and return the exit code."""
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command == "init":
        return _cmd_init(args)
    if args.command == "assess":
        return _cmd_assess(args)
    if args.command == "report":
        return _cmd_report(args)
    if args.command == "generate":
        return _cmd_generate(args)
    if args.command == "breach":
        return _cmd_breach(args)
    if args.command == "evidence":
        return _cmd_evidence(args)
    if args.command == "conditions":
        return _cmd_conditions()
    if args.command == "sections":
        return _cmd_sections(args)
    if args.command == "gdpr-map":
        return _cmd_gdpr_map(args)
    if args.command == "requests":
        return _cmd_requests(args)
    parser.error(f"unknown command: {args.command}")
    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
