#!/usr/bin/env python3
"""Apply the Polish Advanced-menu patch directly to a CS7T-14C026-CD VBF."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from localize_advanced_pl import (  # noqa: E402
    PatchError,
    build as localize_payload,
)
from vbf_tool import Vbf, build as build_vbf  # noqa: E402


PART_NUMBER = "CS7T-14C026-CD"
PAYLOAD_ADDRESS = 0x5000
PAYLOAD_LENGTH = 0xFB000


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_vbf", type=Path, help="your own M0RTAR CD VBF")
    parser.add_argument("output_vbf", type=Path, help="localized CD VBF")
    parser.add_argument(
        "--strict-hash",
        action="store_true",
        help="accept only the two reference payload SHA-256 values",
    )
    args = parser.parse_args(argv)

    try:
        source = Vbf(args.input_vbf)
        errors = source.check()
        hard_errors = [error for error in errors if not error.startswith("file_checksum:")]
        if hard_errors:
            raise PatchError("input VBF validation errors: " + "; ".join(hard_errors))
        if source.part_number != PART_NUMBER:
            raise PatchError(
                f"wrong software partition: {source.part_number!r}; "
                f"expected {PART_NUMBER!r}"
            )
        if source.addr != PAYLOAD_ADDRESS or source.length != PAYLOAD_LENGTH:
            raise PatchError(
                f"wrong block: addr=0x{source.addr:X}, length=0x{source.length:X}; "
                f"expected addr=0x{PAYLOAD_ADDRESS:X}, length=0x{PAYLOAD_LENGTH:X}"
            )
        digest = hashlib.sha256(source.payload).hexdigest()
        patched, report = localize_payload(
            source.payload,
            strict_hash=args.strict_hash,
        )
        _, checksum, size = build_vbf(args.input_vbf, patched, args.output_vbf)
        result = Vbf(args.output_vbf)
        post_errors = result.check()
        if post_errors:
            raise PatchError("output VBF verification failed: " + "; ".join(post_errors))
    except (OSError, PatchError, ValueError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    print(f"OK: wrote {args.output_vbf} ({size} B)")
    print(f"file checksum: 0x{checksum:08X}")
    print(f"output payload SHA-256: {report['output_sha256']}")
    print(f"variant: {report['variant']}")
    for item in report["translated"]:
        print(f"translated {item['field']}: {item['from']} -> {item['to']}")
    for item in report["untranslated"]:
        print(f"UNTRANSLATED {item['field']}: {item['label']}")
    if errors:
        print("NOTE: input header file_checksum was stale; the output checksum was rebuilt.")
    print("Only the CD VBF is changed; ED and bootloader are not required by this patch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
