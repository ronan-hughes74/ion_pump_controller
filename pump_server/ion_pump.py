@final
class IonPump:
    """Python (AnyIO) bindings for an ion pump device."""

    BAUD_RATE: Final = 9600  # Use correct baud rate

    def __init__(self, port: AnyIOSerialPort) -> None:
        self._serial: Final = port

    async def get_status(self) -> str:
        return await self._serial.query("STATUS?")

    async def get_pressure(self) -> float:
        resp = await self._serial.query("PRESSURE?")
        return float(resp.strip())

    async def turn_on(self) -> None:
        await self._serial.query("PUMP ON")

    async def turn_off(self) -> None:
        await self._serial.query("PUMP OFF")

