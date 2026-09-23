import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from localize_advanced_pl import (  # noqa: E402
    BASE,
    FIVE_STRING_BASE,
    FIRST_ITEM_REL,
    ITEM_STRIDE,
    NEW_BASE,
    SRC_START,
    TABLE_POINTER_REL,
    build,
)


class LocalizeAdvancedTests(unittest.TestCase):
    def make_image(self) -> bytearray:
        data = bytearray(0xFB000)
        data[NEW_BASE - BASE : NEW_BASE - BASE + 0x500] = bytes([0xEF]) * 0x500
        h = SRC_START + 0x40
        struct.pack_into(">I", data, h - BASE, 0x006B0007)
        struct.pack_into(">HH", data, h - BASE + 0x3C, 4, 4)
        labels = (
            "Advanced",
            "Digital speed",
            "Engine temp & Voltage",
            "on main",
            "in standby",
        )
        for index, label in enumerate(labels):
            address = 0x10000 + index * 0x20
            data[address - BASE : address - BASE + len(label) + 1] = (
                label.encode("ascii") + b"\0"
            )
        for lang in range(12):
            struct.pack_into(">I", data, h - BASE + 4 + lang * 4, 0x10000)
        for i, item_type in enumerate((0x37, 0x20, 0x37, 0x37)):
            record = h + 0x7C + i * ITEM_STRIDE
            struct.pack_into(">I", data, record - BASE, item_type)
            for lang in range(11):
                struct.pack_into(
                    ">I", data, record - BASE + 4 + lang * 4, 0x10020 + i * 0x20
                )
        target = SRC_START + TABLE_POINTER_REL
        for address in (0x4B398, 0x4C070):
            struct.pack_into(">I", data, address - BASE, target)
        return data

    def make_five_item_image(self) -> bytearray:
        data = bytearray(0xFB000)
        string_end = FIVE_STRING_BASE + 0x200
        data[NEW_BASE - BASE : string_end - BASE] = bytes([0xEF]) * (
            string_end - NEW_BASE
        )
        h = NEW_BASE + 0x40
        struct.pack_into(">I", data, h - BASE, 0x006B0007)
        struct.pack_into(">HH", data, h - BASE + 0x3C, 5, 5)
        labels = (
            "Advanced",
            "Digital speed",
            "Gauge sweep",
            "Engine temp & Voltage",
            "on main",
            "in standby",
        )
        for index, label in enumerate(labels):
            address = 0x10000 + index * 0x20
            data[address - BASE : address - BASE + len(label) + 1] = (
                label.encode("ascii") + b"\0"
            )
        for lang in range(12):
            struct.pack_into(">I", data, h - BASE + 4 + lang * 4, 0x10000)
        for i, item_type in enumerate((0x37, 0x37, 0x20, 0x37, 0x37)):
            record = h + 0x7C + i * ITEM_STRIDE
            struct.pack_into(">I", data, record - BASE, item_type)
            for lang in range(11):
                struct.pack_into(
                    ">I", data, record - BASE + 4 + lang * 4, 0x10020 + i * 0x20
                )
        target = NEW_BASE + TABLE_POINTER_REL
        for address in (0x4B398, 0x4C070):
            struct.pack_into(">I", data, address - BASE, target)
        return data

    def test_localizes_without_changing_item_count(self):
        source = bytes(self.make_image())
        output, report = build(source)
        self.assertEqual(report["changed_bytes"] > 0, True)
        new_h = NEW_BASE + 0x40
        self.assertEqual(output[new_h - BASE : new_h - BASE + 4], bytes.fromhex("006B0007"))
        self.assertEqual(struct.unpack_from(">HH", output, new_h - BASE + 0x3C), (4, 4))
        self.assertEqual(output[0x4B398 - BASE : 0x4B39C - BASE], struct.pack(">I", NEW_BASE + TABLE_POINTER_REL))
        self.assertIn(b"Zaawansowane\0", output)
        self.assertIn(b"Predkosc cyfrowa\0", output)
        self.assertIn(b"Temp. silnika i napiecie\0", output)

    def test_localizes_existing_five_item_gauge_sweep_menu(self):
        source = bytes(self.make_five_item_image())
        output, report = build(source)
        self.assertEqual(report["item_count"], 5)
        self.assertEqual(report["gauge_sweep_present"], True)
        h = NEW_BASE + 0x40
        self.assertEqual(struct.unpack_from(">HH", output, h - BASE + 0x3C), (5, 5))
        self.assertIn(b"Test wskazowek\0", output)
        self.assertIn(b"Temp. silnika i napiecie\0", output)

    def test_reports_and_preserves_an_unknown_extra_item(self):
        source = self.make_five_item_image()
        h = NEW_BASE + 0x40
        struct.pack_into(">HH", source, h - BASE + 0x3C, 6, 6)
        record = h + 0x7C + 5 * ITEM_STRIDE
        struct.pack_into(">I", source, record - BASE, 0x37)
        unknown_address = 0x10100
        unknown_label = b"New future option\0"
        source[unknown_address - BASE : unknown_address - BASE + len(unknown_label)] = (
            unknown_label
        )
        for lang in range(11):
            struct.pack_into(
                ">I", source, record - BASE + 4 + lang * 4, unknown_address
            )

        output, report = build(bytes(source))
        self.assertEqual(report["item_count"], 6)
        self.assertEqual(report["untranslated"], [{"field": "item_5", "label": "New future option"}])
        self.assertIn(b"Test wskazowek\0", output)
        self.assertEqual(
            struct.unpack_from(">I", output, record - BASE + 4)[0], unknown_address
        )

    def test_hash_gate_rejects_unknown_variant(self):
        with self.assertRaises(Exception):
            build(bytes(self.make_five_item_image()), verify_hash=True)

    def test_refuses_stock_like_image(self):
        with self.assertRaises(Exception):
            build(bytes(0xFB000))


if __name__ == "__main__":
    unittest.main()
