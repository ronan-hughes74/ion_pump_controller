from typing import Final, final
import anyio_serial
from pydux.control_support.pyserial_extensions import AnyIOSerialPort

@final
class IonPump:
    """Async interface to the ion pump device over serial (AnyIO compatible).

    The pump communicates via a simple ASCII protocol using fixed-format packets.
    Example packet: "~ 01 0B 7F\r"
    """

    BAUD_RATE: Final = 115200  # Default baud rate for the ion pump

    def __init__(self):
        self.serial = None  # Will be set when connected
        self.connected_port = None
        self._pump_address: int = 1  # Default address (can be changed via setter)

    # --- Core Protocol Utilities ---

    @staticmethod
    def compute_ascii_checksum(data: str) -> int:
        """Compute checksum as sum of ASCII values of the input string."""
        return sum(ord(char) for char in data)

    @staticmethod
    def calculate_checksum(address: int, command: str) -> int:
        """Compute final checksum from address and command fields."""
        address_str = f"{address:02}"
        checksum = (
            IonPump.compute_ascii_checksum(address_str)
            + IonPump.compute_ascii_checksum(command)
            + 32 * 3  # ASCII value for three spaces
        )
        return checksum % 256

    def build_command(self, command: str) -> str:
        """Builds the full packet string to send to the pump."""
        address_str = f"{self._pump_address:02}"
        checksum = self.calculate_checksum(self._pump_address, command)
        return f"~ {address_str} {command} {checksum:02X}"

    # --- Device API Methods ---
    
    async def get_pressure(self) -> float:
        """Query pressure reading from the pump."""
        packet = self.build_command("0B")
        resp = await self.serial.query(packet)
        return float(resp.strip())

    async def get_voltage(self) -> float:
        """Query voltage reading (using simple command format)."""
        packet = self.build_command("vr")
        resp = await self.serial.query(packet)
        return float(resp.strip())

    async def get_current(self) -> float:
        packet = self.build_command("vr")
        resp = await self.serial.query(packet)
        return float(resp.strip())

    # Status is not an actual command, but just a placeholder
    async def get_status(self) -> float:
        packet = self.build_command("status")
        resp = await self.serial.query(packet)
        return float(resp.strip())
        
    # --- Configuration Methods ---

    async def connect_to_port(self, port_name: str) -> None:
        """Connect to the serial port."""
        try:
            # Open the serial port
            async with anyio_serial.Serial(port=port_name, baudrate=IonPump.BAUD_RATE) as raw_port:
                self.serial = AnyIOSerialPort(raw_port, send_delimiter="\r", receive_delimiter="\r", codec="ascii")
                self.connected_port = port_name
                print(f"Connected to {port_name}")
        except Exception as e:
            print(f"Failed to connect to {port_name}: {e}")

    def set_pump_address(self, address: int) -> None:
        """Set the device's address for multi-device setups (0–99)."""
        if not (0 <= address <= 255):
            raise ValueError("Pump address must be between 0 and 99.")
        self._pump_address = address

    def get_pump_address(self) -> int:
        """Return the current pump address."""
        return self._pump_address
