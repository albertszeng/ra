import struct

_MAX_FLOAT_LENGTH = 5


def compress(floats: tuple[float, ...]) -> int:
    if len(floats) > _MAX_FLOAT_LENGTH:
        raise ValueError("Input must be a list of at most 4 floats.")
    if len(floats) < _MAX_FLOAT_LENGTH:
        floats = floats + (0.0,) * (_MAX_FLOAT_LENGTH - len(floats))
    packed = struct.pack("<" + "e" * len(floats), *floats)
    return int.from_bytes(packed, byteorder="little")


def decompress(packed: int) -> tuple[float, ...]:
    bytes = packed.to_bytes(
        struct.calcsize("<" + "e" * _MAX_FLOAT_LENGTH), byteorder="little"
    )
    return struct.unpack("<" + "e" * _MAX_FLOAT_LENGTH, bytes)
