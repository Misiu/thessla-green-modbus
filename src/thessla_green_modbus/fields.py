"""Device-specific fields not represented by standard packed Modbus strings."""

from modbus_connection.model import RegisterField


class SerialNumberField(RegisterField[str]):
    """Six registers each containing one byte, not three packed registers.

    The manufacturer's example 001a 002b 003c 004d 005e 006f represents
    serial number 1a2b3c4d5e6f. Missing/unprogrammed or malformed IDs are unknown.
    """

    def __init__(self, address: int) -> None:
        super().__init__(address, count=6)

    def decode(self, words: list[int], scale_exponent: int | None = None) -> str | None:
        if (
            len(words) != 6
            or any(not 0 <= word <= 255 for word in words)
            or all(word == 0 for word in words)
            or all(word == 255 for word in words)
        ):
            return None
        return "".join(f"{word:02x}" for word in words)
