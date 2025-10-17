"""Command line interface for converting architectural plans into VR scenes."""
from __future__ import annotations

import argparse
from pathlib import Path

from vrhouse.core import SceneSpecification
from vrhouse.pipeline.importers.multi_importer import iter_supported_suffixes, validate_source_path
from vrhouse.pipeline.runner import run_conversion


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert 3D house plans into VR experiences")
    formats = ", ".join(sorted({ext for ext in iter_supported_suffixes()}))
    parser.add_argument("source", type=Path, help=f"Path to the 3D model ({formats})")
    parser.add_argument("project_name", type=str, help="Name of the VR project")
    parser.add_argument("output", type=Path, help="Directory to store VR exports")
    parser.add_argument("--no-physics", action="store_true", help="Disable physics inference")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI material enhancement")
    parser.add_argument(
        "--encryption-key",
        type=str,
        default=None,
        help="Base64 key to encrypt the package. A new key is generated if omitted.",
    )
    return parser


def run_cli(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    validate_source_path(args.source)

    specification = SceneSpecification(
        project_name=args.project_name,
        source_file=args.source,
        enable_physics=not args.no_physics,
        enable_ai_realism=not args.no_ai,
        output_encryption_key=args.encryption_key,
    )

    result = run_conversion(specification, args.output)

    parser.exit(
        message=(
            "VR scene exported to {path}\nEncryption key: {key}\n".format(
                path=result["package_path"],
                key=result["encryption_key"],
            )
        )
    )


if __name__ == "__main__":
    run_cli()
