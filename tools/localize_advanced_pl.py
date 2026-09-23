#!/usr/bin/env python3
"""Translate the existing M0RTAR Advanced menu.

The tool works on the raw 0x5000-based CS7T-14C026-CD payload. It supports the
original four-item menu and an existing relocated menu with Gauge Sweep or
other additional records. It does not add a menu item or change measurement
code: it only translates labels it recognizes and reports any other labels.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path


BASE = 0x5000
PAYLOAD_LENGTH = 0xFB000
EXPECTED_BASE_SHA256 = (
    "9c4b3b051a9dd1705d2acd27658d25fb71a52f5c2a20f5595f4885016a3661a1"
)
EXPECTED_FIVE_ITEM_SHA256 = (
    "0c91f7e940b4e48c729a5f8b0a788c2296fb51c645c1a18db60e76c3497dd034"
)
SUPPORTED_BASE_SHA256 = {
    EXPECTED_BASE_SHA256: "oryginalne menu M0RTAR, 4 pozycje",
    EXPECTED_FIVE_ITEM_SHA256: "wariant z Gauge Sweep, 5 pozycji",
}

SRC_START = 0x0DD200
SRC_END = 0x0DD3EC
NEW_BASE = 0x0DDD00
HEADER_REL = 0x40
TABLE_POINTER_REL = HEADER_REL + 0x34
COUNT_REL = HEADER_REL + 0x3C
FIRST_ITEM_REL = HEADER_REL + 0x7C
ITEM_STRIDE = 0x48
SLOT = 0x20
FILL = 0xEF
MENU_SIGNATURE = 0x006B0007
FIVE_STRING_BASE = 0x0DDF60
SCREEN_POINTER_ADDRESSES = (0x04B398, 0x04C070)

FOUR_ITEM_LABELS = (
    "Zaawansowane",
    "Predkosc cyfrowa",
    "Temp. silnika i napiecie",
    "Na ekranie glownym",
    "W trybie czuwania",
)
FIVE_ITEM_LABELS = (
    "Zaawansowane",
    "Predkosc cyfrowa",
    "Test wskazowek",
    "Temp. silnika i napiecie",
    "Na ekranie glownym",
    "W trybie czuwania",
)

# Backwards-compatible name for callers that used the original four-label
# patch.  The active label set is selected by the detected menu variant.
LABELS = FOUR_ITEM_LABELS

# The firmware stores several language pointers for every label.  We use the
# readable English/ASCII variant when identifying an item, but accept the
# already-localized form too so that a mixed menu can be completed safely.
TRANSLATIONS = {
    "advanced": "Zaawansowane",
    "zaawansowane": "Zaawansowane",
    "digital speed": "Predkosc cyfrowa",
    "predkosc cyfrowa": "Predkosc cyfrowa",
    "gauge sweep": "Test wskazowek",
    "test wskazowek": "Test wskazowek",
    "engine temp & voltage": "Temp. silnika i napiecie",
    "temp. silnika i napiecie": "Temp. silnika i napiecie",
    "on main": "Na ekranie glownym",
    "na ekranie glownym": "Na ekranie glownym",
    "in standby": "W trybie czuwania",
    "w trybie czuwania": "W trybie czuwania",
}


class PatchError(RuntimeError):
    """A deliberate compatibility or safety refusal."""


def _u16(blob: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from(">H", blob, offset)[0]


def _u32(blob: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from(">I", blob, offset)[0]


def _put32(blob: bytearray, offset: int, value: int) -> None:
    struct.pack_into(">I", blob, offset, value)


def _payload_offset(address: int) -> int:
    return address - BASE


def _normalize_label(label: str) -> str:
    return " ".join(label.strip().lower().split())


def _read_ascii_label(data: bytes | bytearray, address: int) -> str | None:
    """Read one printable label slot, returning None for non-text data."""

    offset = _payload_offset(address)
    if offset < 0 or offset >= len(data):
        return None
    raw = bytes(data[offset : offset + SLOT])
    raw = raw.split(b"\x00", 1)[0]
    if not raw or any(byte < 0x20 or byte > 0x7E for byte in raw):
        return None
    return raw.decode("ascii")


def _read_language_label(
    data: bytes | bytearray,
    descriptor_base: int,
    pointer_offset: int,
    pointer_count: int,
) -> str | None:
    """Return the first readable language/fallback string for a field."""

    for index in range(pointer_count):
        pointer = _u32(data, _payload_offset(descriptor_base + pointer_offset + index * 4))
        label = _read_ascii_label(data, pointer)
        if label is not None:
            return label
    return None


def _translate_label(label: str | None) -> str | None:
    if label is None:
        return None
    return TRANSLATIONS.get(_normalize_label(label))


def _menu_labels(
    data: bytes | bytearray,
    descriptor_base: int,
    item_count: int,
) -> tuple[str | None, list[str | None]]:
    """Inspect the title and every item without trusting its visible order."""

    title = _read_language_label(data, descriptor_base, HEADER_REL + 4, 12)
    labels: list[str | None] = []
    for item_index in range(item_count):
        record = descriptor_base + FIRST_ITEM_REL + item_index * ITEM_STRIDE
        labels.append(_read_language_label(data, record, 4, 11))
    return title, labels


def _translation_plan(
    title: str | None,
    item_labels: list[str | None],
) -> tuple[list[int | None], list[tuple[str, str, str]], list[tuple[str, str]]]:
    """Build pointer targets, translated entries and untranslated entries."""

    pointer_targets: list[int | None] = [None] * (1 + len(item_labels))
    translated: list[tuple[str, str, str]] = []
    untranslated: list[tuple[str, str]] = []

    fields: list[tuple[str, str | None]] = [("title", title)]
    fields.extend(
        (f"item_{index}", label) for index, label in enumerate(item_labels)
    )
    for field, source_label in fields:
        target = _translate_label(source_label)
        if target is None:
            untranslated.append((field, source_label or "<nieodczytana etykieta>"))
            continue
        logical_index = 0 if field == "title" else int(field.split("_", 1)[1]) + 1
        pointer_targets[logical_index] = -1  # filled with an address later
        translated.append((field, source_label or "<nieodczytana etykieta>", target))
    return pointer_targets, translated, untranslated


def _find_screen_pointer_slots(
    data: bytes | bytearray,
    descriptor_base: int,
    excluded_range: tuple[int, int],
) -> list[int]:
    """Return payload offsets that point to one menu descriptor table."""

    target = descriptor_base + TABLE_POINTER_REL
    source_lo = _payload_offset(excluded_range[0])
    source_hi = _payload_offset(excluded_range[1])
    slots: list[int] = []
    for offset in range(0, len(data) - 3, 2):
        if _u32(data, offset) != target:
            continue
        if source_lo <= offset < source_hi:
            continue
        slots.append(offset)
    return slots


def _active_descriptor_base(data: bytes | bytearray) -> int:
    """Resolve the descriptor currently selected by both known screen tables."""

    pointers = [
        _u32(data, _payload_offset(address)) for address in SCREEN_POINTER_ADDRESSES
    ]
    if pointers[0] != pointers[1]:
        raise PatchError(
            "the two Advanced-menu screen pointers do not select the same descriptor"
        )
    descriptor_base = pointers[0] - TABLE_POINTER_REL
    if descriptor_base < BASE or descriptor_base >= BASE + PAYLOAD_LENGTH:
        raise PatchError(
            f"Advanced-menu descriptor pointer resolves outside the payload: "
            f"0x{descriptor_base:X}"
        )
    return descriptor_base


def _validate_records(
    data: bytes | bytearray,
    descriptor_base: int,
    item_count: int,
    descriptor_end: int,
) -> None:
    """Validate the M0RTAR header, count and record types."""

    header = descriptor_base + HEADER_REL
    if _u32(data, _payload_offset(header)) != MENU_SIGNATURE:
        found = _u32(data, _payload_offset(header))
        raise PatchError(
            f"M0RTAR Advanced header missing at 0x{header:X} "
            f"(found 0x{found:08X})"
        )

    count_a = _u16(data, _payload_offset(header + 0x3C))
    count_b = _u16(data, _payload_offset(header + 0x3C + 2))
    if (count_a, count_b) != (item_count, item_count):
        raise PatchError(
            f"unexpected Advanced-menu counts at 0x{header + 0x3C:X}: "
            f"{count_a}/{count_b}; expected {item_count}/{item_count}"
        )

    first_item = descriptor_base + FIRST_ITEM_REL
    for item_index in range(item_count):
        record = first_item + item_index * ITEM_STRIDE
        if record + ITEM_STRIDE > descriptor_end:
            raise PatchError(f"menu record {item_index} exceeds descriptor")
        item_type = _u32(data, _payload_offset(record))
        if item_type not in (0x20, 0x37):
            raise PatchError(
                f"unexpected menu record type at item {item_index}: 0x{item_type:X}"
            )


def _write_label_pointers(
    block: bytearray,
    item_count: int,
    label_addresses: list[int | None],
) -> None:
    """Write title and item language/fallback pointers in one descriptor."""

    # Twelve title-language/fallback pointers.
    if label_addresses[0] is not None:
        for index in range(12):
            _put32(block, HEADER_REL + 4 + index * 4, label_addresses[0])

    # Eleven language pointers per menu record.
    for item_index in range(item_count):
        label_address = label_addresses[item_index + 1]
        if label_address is None:
            continue
        record = FIRST_ITEM_REL + item_index * ITEM_STRIDE
        for language_index in range(11):
            _put32(
                block,
                record + 4 + language_index * 4,
                label_address,
            )


def _encode_labels(labels: tuple[str, ...]) -> bytes:
    strings = bytearray()
    for label in labels:
        encoded = label.encode("ascii")
        if len(encoded) >= SLOT:
            raise PatchError(f"label is too long for a 0x{SLOT:X}-byte slot: {label}")
        strings.extend(encoded)
        strings.extend(bytes(SLOT - len(encoded)))
    return bytes(strings)


def _build_four_item(data: bytes, *, new_base: int) -> tuple[bytes, dict[str, object]]:
    """Clone and localize the original four-item descriptor."""

    source_offset = _payload_offset(SRC_START)
    source_end_offset = _payload_offset(SRC_END)
    source_length = source_end_offset - source_offset
    source = data[source_offset:source_end_offset]
    _validate_records(data, SRC_START, 4, SRC_END)
    detected_title, detected_items = _menu_labels(data, SRC_START, 4)
    _, translated, untranslated = _translation_plan(
        detected_title, detected_items
    )
    if not translated:
        raise PatchError(
            "no known Advanced-menu labels found; nothing was translated"
        )

    slots = _find_screen_pointer_slots(data, SRC_START, (SRC_START, SRC_END))
    if len(slots) < 2:
        raise PatchError(
            "could not find both screen-table pointers to the M0RTAR descriptor"
        )

    label_start = new_base + ((source_length + 3) & ~3)
    translated_labels = tuple(entry[2] for entry in translated)
    total_length = (label_start - new_base) + len(translated_labels) * SLOT
    new_offset = _payload_offset(new_base)
    if new_offset < 0 or new_offset + total_length > len(data):
        raise PatchError("localized descriptor would exceed the payload")
    if data[new_offset : new_offset + total_length] != bytes([FILL]) * total_length:
        raise PatchError(
            f"target area 0x{new_base:X}..0x{new_base + total_length:X} "
            "is not empty 0xEF"
        )

    block = bytearray(source)
    delta = new_base - SRC_START
    relocated_pointers = 0
    for offset in range(0, len(block) - 3, 4):
        value = _u32(block, offset)
        if SRC_START <= value < SRC_END:
            _put32(block, offset, value + delta)
            relocated_pointers += 1

    label_addresses: list[int | None] = [None] * 5
    for index, (field, _, _) in enumerate(translated):
        logical_index = 0 if field == "title" else int(field.split("_", 1)[1]) + 1
        label_addresses[logical_index] = label_start + index * SLOT
    _write_label_pointers(block, 4, label_addresses)
    strings = _encode_labels(translated_labels)

    output = bytearray(data)
    output[new_offset : new_offset + len(block)] = block
    string_offset = _payload_offset(label_start)
    output[string_offset : string_offset + len(strings)] = strings

    new_table_target = new_base + TABLE_POINTER_REL
    for slot in slots:
        _put32(output, slot, new_table_target)

    if _u32(output, _payload_offset(new_base + HEADER_REL)) != MENU_SIGNATURE:
        raise PatchError("localized descriptor header verification failed")
    if (
        _u16(output, _payload_offset(new_base + COUNT_REL)),
        _u16(output, _payload_offset(new_base + COUNT_REL + 2)),
    ) != (4, 4):
        raise PatchError("localized descriptor count verification failed")

    changed_bytes = sum(left != right for left, right in zip(data, output))
    report = {
        "variant": "four-item M0RTAR",
        "item_count": 4,
        "gauge_sweep_present": any(
            _normalize_label(label or "") in ("gauge sweep", "test wskazowek")
            for label in detected_items
        ),
        "base_sha256": hashlib.sha256(data).hexdigest(),
        "output_sha256": hashlib.sha256(output).hexdigest(),
        "source_descriptor": f"0x{SRC_START:X}..0x{SRC_END:X}",
        "new_descriptor": f"0x{new_base:X}..0x{new_base + total_length:X}",
        "screen_pointer_slots": [f"0x{slot + BASE:X}" for slot in slots],
        "relocated_internal_pointers": relocated_pointers,
        "changed_bytes": changed_bytes,
        "detected_title": detected_title,
        "detected_items": detected_items,
        "translated": [
            {"field": field, "from": source_label, "to": target}
            for field, source_label, target in translated
        ],
        "untranslated": [
            {"field": field, "label": label} for field, label in untranslated
        ],
        "labels": list(translated_labels),
    }
    return bytes(output), report


def _build_existing_menu(data: bytes, *, item_count: int) -> tuple[bytes, dict[str, object]]:
    """Localize an existing cloned Advanced menu without changing its records."""

    record_end = NEW_BASE + FIRST_ITEM_REL + item_count * ITEM_STRIDE
    label_start = max(FIVE_STRING_BASE, (record_end + 3) & ~3)
    if label_start <= NEW_BASE or label_start > BASE + len(data):
        raise PatchError("invalid Advanced-menu string area")
    _validate_records(data, NEW_BASE, item_count, label_start)
    detected_title, detected_items = _menu_labels(data, NEW_BASE, item_count)
    _, translated, untranslated = _translation_plan(
        detected_title, detected_items
    )
    if not translated:
        raise PatchError(
            "no known Advanced-menu labels found; nothing was translated"
        )

    slots = _find_screen_pointer_slots(
        data,
        NEW_BASE,
        (NEW_BASE, label_start),
    )
    if len(slots) < 2:
        raise PatchError(
            "could not find both screen-table pointers to the five-item descriptor"
        )

    translated_labels = tuple(entry[2] for entry in translated)
    strings = _encode_labels(translated_labels)
    string_offset = _payload_offset(label_start)
    if string_offset < 0 or string_offset + len(strings) > len(data):
        raise PatchError("five-item label area would exceed the payload")
    if data[string_offset : string_offset + len(strings)] != bytes([FILL]) * len(strings):
        raise PatchError(
            f"five-item label area 0x{label_start:X}.."
            f"0x{label_start + len(strings):X} is not empty 0xEF"
        )

    block_start = _payload_offset(NEW_BASE)
    block_end = _payload_offset(label_start)
    block = bytearray(data[block_start:block_end])
    label_addresses: list[int | None] = [None] * (1 + item_count)
    for index, (field, _, _) in enumerate(translated):
        logical_index = 0 if field == "title" else int(field.split("_", 1)[1]) + 1
        label_addresses[logical_index] = label_start + index * SLOT
    _write_label_pointers(block, item_count, label_addresses)

    output = bytearray(data)
    output[block_start:block_end] = block
    output[string_offset : string_offset + len(strings)] = strings

    if _u32(output, _payload_offset(NEW_BASE + HEADER_REL)) != MENU_SIGNATURE:
        raise PatchError("five-item descriptor header verification failed")
    if (
        _u16(output, _payload_offset(NEW_BASE + COUNT_REL)),
        _u16(output, _payload_offset(NEW_BASE + COUNT_REL + 2)),
    ) != (item_count, item_count):
        raise PatchError("five-item descriptor count verification failed")

    changed_bytes = sum(left != right for left, right in zip(data, output))
    gauge_sweep_present = any(
        _normalize_label(label or "") in ("gauge sweep", "test wskazowek")
        for label in detected_items
    )
    report = {
        "variant": (
            f"{item_count}-item Gauge Sweep"
            if gauge_sweep_present
            else f"existing Advanced menu ({item_count} items)"
        ),
        "item_count": item_count,
        "gauge_sweep_present": gauge_sweep_present,
        "base_sha256": hashlib.sha256(data).hexdigest(),
        "output_sha256": hashlib.sha256(output).hexdigest(),
        "source_descriptor": f"0x{NEW_BASE:X}..0x{label_start:X}",
        "new_descriptor": "existing Advanced-menu descriptor (not relocated)",
        "screen_pointer_slots": [f"0x{slot + BASE:X}" for slot in slots],
        "relocated_internal_pointers": 0,
        "changed_bytes": changed_bytes,
        "detected_title": detected_title,
        "detected_items": detected_items,
        "translated": [
            {"field": field, "from": source_label, "to": target}
            for field, source_label, target in translated
        ],
        "untranslated": [
            {"field": field, "label": label} for field, label in untranslated
        ],
        "labels": list(translated_labels),
    }
    return bytes(output), report


def build(
    data: bytes,
    *,
    new_base: int = NEW_BASE,
    strict_hash: bool = False,
    verify_hash: bool | None = None,
) -> tuple[bytes, dict[str, object]]:
    """Return a localized payload and a machine-readable change report.

    By default the active menu is identified structurally, so a compatible
    Bluetooth or other code patch does not invalidate localization.  Set
    ``strict_hash`` (or the legacy alias ``verify_hash``) to limit the input to
    the two reference payload hashes documented in the project.
    """

    if verify_hash is not None:
        strict_hash = verify_hash

    if len(data) != PAYLOAD_LENGTH:
        raise PatchError(
            f"wrong payload length: 0x{len(data):X}; expected 0x{PAYLOAD_LENGTH:X}"
        )
    if not (BASE <= SRC_START < SRC_END <= BASE + len(data)):
        raise PatchError("source descriptor is outside the payload")
    if new_base < BASE or new_base >= BASE + len(data):
        raise PatchError("new descriptor address is outside the payload")

    digest = hashlib.sha256(data).hexdigest()
    if strict_hash and digest not in SUPPORTED_BASE_SHA256:
        expected = "\n".join(
            f"  {value}: {description}"
            for value, description in SUPPORTED_BASE_SHA256.items()
        )
        raise PatchError(
            "base SHA-256 mismatch; this public patch targets one of these "
            f"known M0RTAR 1412-FL payloads\n  found: {digest}\n{expected}"
        )

    active_base = _active_descriptor_base(data)
    item_count = _u16(data, _payload_offset(active_base + COUNT_REL))

    if active_base == SRC_START:
        if item_count != 4:
            raise PatchError(
                f"the original descriptor has {item_count} items; "
                "only the standard four-item source layout can be cloned safely"
            )
        return _build_four_item(data, new_base=new_base)

    if active_base == NEW_BASE:
        if item_count < 5:
            raise PatchError(
                f"the relocated descriptor has only {item_count} items; "
                "expected a menu extended by Gauge Sweep or another item"
            )
        if new_base != NEW_BASE:
            raise PatchError("an existing relocated menu requires the standard menu address")
        return _build_existing_menu(data, item_count=item_count)

    raise PatchError(
        f"unsupported active Advanced-menu address 0x{active_base:X}; "
        f"expected 0x{SRC_START:X} or 0x{NEW_BASE:X}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_bin", type=Path, help="raw 0x5000-based CD payload")
    parser.add_argument("output_bin", type=Path, help="localized raw payload")
    parser.add_argument(
        "--strict-hash",
        action="store_true",
        help="accept only the two reference payload SHA-256 values",
    )
    args = parser.parse_args(argv)

    try:
        data = args.input_bin.read_bytes()
        output, report = build(data, strict_hash=args.strict_hash)
        args.output_bin.write_bytes(output)
    except (OSError, PatchError, struct.error) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    print(f"OK: wrote {args.output_bin} ({len(output)} B)")
    print(f"changed bytes: {report['changed_bytes']}")
    print(f"output SHA-256: {report['output_sha256']}")
    print(f"variant: {report['variant']}")
    for item in report["translated"]:
        print(f"  przetłumaczono {item['field']}: {item['from']} -> {item['to']}")
    for item in report["untranslated"]:
        print(f"  NIEPRZETŁUMACZONE {item['field']}: {item['label']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
