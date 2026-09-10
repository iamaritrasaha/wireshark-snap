#!/usr/bin/env python3
"""Generate a tiny deterministic Ethernet/IPv4/UDP pcapng fixture."""

from __future__ import annotations

import struct
import sys
from pathlib import Path


def block(block_type: int, body: bytes) -> bytes:
    length = 12 + len(body)
    if length % 4:
        raise ValueError("pcapng block body must be four-byte aligned")
    return struct.pack("<II", block_type, length) + body + struct.pack("<I", length)


def make_fixture() -> bytes:
    section_header = struct.pack("<IHHq", 0x1A2B3C4D, 1, 0, -1)
    interface = struct.pack("<HHI", 1, 0, 65535)

    ethernet = bytes.fromhex(
        "00112233445566778899aabb0800"
        "4500001f1234000040110000c0000201c0000202"
        "30390035000b0000"
        "6869"
    )
    padded_packet = ethernet + b"\0" * ((-len(ethernet)) % 4)
    packet = struct.pack("<IIIII", 0, 0, 1_000_000, len(ethernet), len(ethernet))
    packet += padded_packet

    return b"".join(
        (
            block(0x0A0D0D0A, section_header),
            block(1, interface),
            block(6, packet),
        )
    )


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} OUTPUT.pcapng", file=sys.stderr)
        return 2
    output = Path(sys.argv[1])
    output.write_bytes(make_fixture())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
