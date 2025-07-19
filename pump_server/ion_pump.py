from typing import Final, final
from pydux.control_support.pyserial_extensions import AnyIOSerialPort

@final
class IonPump:
    """Async interface to the ion pump device."""

    BAUD_RATE: Final = 115200  # Default baud rate for pump

    def __init__(self, port: AnyIOSerialPort) -> None:
        self._serial: Final = port

    async def get_pressure(self) -> float:
        resp = await self._serial.query("PR?")
        return float(resp.strip())

    async def turn_on(self) -> None:
        await self._serial.query("ON")

    async def turn_off(self) -> None:
        await self._serial.query("OFF")

    async def get_status(self) -> str:
        return await self._serial.query("STATUS?")
