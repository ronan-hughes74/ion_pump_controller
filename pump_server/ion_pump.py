from typing import Final, final
from pydux.control_support.pyserial_extensions import AnyIOSerialPort

@final
class IonPump:
    """Async interface to the ion pump device."""

    BAUD_RATE: Final = 115200  # Default baud rate for pump

    def __init__(self, port: AnyIOSerialPort) -> None:
        self._serial: Final = port

""" 
get_(value) commands work by sending the values inside the paranthesis ( a string) to the seral device, and returns a response. Right now resp.string removes extra spaces, however I'm not sure if we want that
We need to create logic to calculate the hex code. I will likely create my own function to do this. 
"""
"""
Command Packet Structure:
<START CHAR> <space> <ADDRESS> <space> <COMMAND> <space> <CHECKSUM> <TERMINATOR>
    1. Start Char: ~
    2. Address: 2 bytes
    3. Command: 2 bytes
    4. Checksum: 2 bytes
    5. Terminator: 1 byte
"""

    async def get_pressure(self) -> float:
        resp = await self._serial.query("PR?")
        return float(resp.strip())
        
    async def get_voltage(self) -> float:
        resp = await self.serial.query("VR?")
        return float(resp.strip())
        
    async def get_current(self) -> float:
        resp = await self.serial.query("CR?")
        return float(resp.strip())
        
    async def turn_on(self) -> None:
        await self._serial.query("ON")

    async def turn_off(self) -> None:
        await self._serial.query("OFF")

    async def get_status(self) -> str:
        return await self._serial.query("STATUS?")

    def set_pump_address(self, threshold: float) -> None:
        """Sets the pressure threshold to be used by other methods."""
        self._pump_address = threshold

    def get_pump_address(self) -> float:
        """Returns the current pressure threshold."""
        return self._pump_address
