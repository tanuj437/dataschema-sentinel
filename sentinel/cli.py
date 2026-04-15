"""Command-line interface for Sentinel."""

import argparse
import sys
from pathlib import Path

import sentinel


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DataSchema Sentinel - Schema drift detection for data pipelines"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Compare two schema versions")
    diff_parser.add_argument("name", help="Schema name")
    diff_parser.add_argument("--version1", type=int, help="First version (default: latest-1)")
    diff_parser.add_argument("--version2", type=int, help="Second version (default: latest)")
    diff_parser.set_defaults(func=cmd_diff)

    # history command
    history_parser = subparsers.add_parser("history", help="Show schema version history")
    history_parser.add_argument("name", help="Schema name")
    history_parser.add_argument("--last", type=int, default=10, help="Show last N versions")
    history_parser.set_defaults(func=cmd_history)

    # list command
    list_parser = subparsers.add_parser("list", help="List all tracked schemas")
    list_parser.set_defaults(func=cmd_list)

    # export command
    export_parser = subparsers.add_parser("export", help="Export schema snapshot")
    export_parser.add_argument("name", help="Schema name")
    export_parser.add_argument("--version", type=int, help="Version to export (default: latest)")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json")
    export_parser.set_defaults(func=cmd_export)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_diff(args):
    """Handle diff command."""
    instance = sentinel.get_instance()
    events = instance.diff(args.name, args.version1 or 1, args.version2 or 2)

    if not events:
        print(f"No differences between versions")
        return

    for event in events:
        print(f"[{event.severity.value}] {event.column}: {event.message}")


def cmd_history(args):
    """Handle history command."""
    instance = sentinel.get_instance()
    snapshots = instance.history(args.name, args.last)

    print(f"\nSchema history for '{args.name}':")
    print("-" * 70)
    for snap in snapshots:
        print(f"  v{snap.version:3d} | {snap.captured_at.isoformat()} | {snap.row_count:8,} rows | {len(snap.columns):3d} cols")


def cmd_list(args):
    """Handle list command."""
    instance = sentinel.get_instance()
    schemas = instance.list_schemas()

    print(f"Tracked schemas ({len(schemas)}):")
    for schema in schemas:
        print(f"  - {schema}")


def cmd_export(args):
    """Handle export command."""
    instance = sentinel.get_instance()
    snap = instance.store.load_latest(args.name) if not args.version else instance.store.load_version(args.name, args.version)

    if not snap:
        print(f"Schema '{args.name}' not found")
        sys.exit(1)

    if args.format == "json":
        import json
        print(json.dumps(snap.to_dict(), indent=2))
    else:
        # CSV export
        print("column,dtype,nullable,null_count,null_pct,unique_count")
        for col_name, col_profile in snap.columns.items():
            print(f"{col_name},{col_profile.dtype},{col_profile.nullable},{col_profile.null_count},{col_profile.null_pct},{col_profile.unique_count or 'N/A'}")


if __name__ == "__main__":
    main()
