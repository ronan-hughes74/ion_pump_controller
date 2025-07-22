# --- Standard Library Imports ---
from typing import Final, final  # For class-level constants and immutability

# --- Third-Party Imports ---
import anyio_serial                                # AnyIO-compatible serial I/O
from pydux.control_support.pyserial_extensions import AnyIOSerialPort  # Delimited async serial port wrapper

# --- Ion Pump Class ---
@final
class IonPump:
    """
    Async interface to the ion pump device over serial (AnyIO compatible).
    
    The pump communicates using a simple ASCII-based protocol with
    fixed-format packets. Example: "~ 01 0B 7F\r"
    """

    BAUD_RATE: Final = 115200  # Default serial communication speed

    def __init__(self):
        self.serial = None                 # Will hold the active serial port object
        self.connected_port = None         # Port name string (e.g., COM3 or /dev/ttyUSB0)
        self._pump_address: int = 1        # Default address of pump (can be changed)

    # -------------------------------------------------------------------------
    # 🔧 Low-Level Protocol Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def compute_ascii_checksum(data: str) -> int:
        """
        Compute checksum as sum of ASCII values in a string.

        Args:
            data (str): Input ASCII string

        Returns:
            int: Raw sum of ASCII values
        """
        return sum(ord(char) for char in data)

    @staticmethod
    def calculate_checksum(address: int, command: str) -> int:
        """
        Computes a final packet checksum using address and command fields.

        Args:
            address (int): Pump address (0–99)
            command (str): 2-character command code

        Returns:
            int: Modulo-256 checksum value
        """
        address_str = f"{address:02}"
        checksum = (
            IonPump.compute_ascii_checksum(address_str)
            + IonPump.compute_ascii_checksum(command)
            + 32 * 3  # ASCII for three spaces
        )
        return checksum % 256

    def build_command(self, command: str) -> str:
        """
        Constructs a complete command packet for the pump.

        Args:
            command (str): Pump command (e.g., "0B")

        Returns:
            str: Full ASCII command string with checksum
        """
        address_str = f"{self._pump_address:02}"
        checksum = self.calculate_checksum(self._pump_address, command)
        return f"~ {address_str} {command} {checksum:02X}"

    # -------------------------------------------------------------------------
    # 📡 Device API Methods
    # -------------------------------------------------------------------------

    async def get_pressure(self) -> float:
        """
        Queries the pressure reading from the pump.

        Returns:
            float: Pressure value as reported by the pump
        """
        packet = self.build_command("0B")
        resp = await self.serial.query(packet)
        return float(resp.strip())

    async def get_voltage(self) -> float:
        """
        Queries the voltage reading from the pump.

        Returns:
            float: Voltage value as reported by the pump
        """
        packet = self.build_command("vr")
        resp = await self.serial.query(packet)
        return float(resp.strip())

    async def get_current(self) -> float:
        """
        Queries the current reading from the pump.

        Returns:
            float: Current value as reported by the pump
        """
        packet = self.build_command("vr")
        resp = await self.serial.query(packet)
        return float(resp.strip())

    async def get_status(self) -> float:
        """
        Queries a status value from the pump. Currently a placeholder.

        Returns:
            float: Status value
        """
        packet = self.build_command("status")
        resp = await self.serial.query(packet)
        return float(resp.strip())

    # -------------------------------------------------------------------------
    # 🔌 Connection and Configuration Methods
    # -------------------------------------------------------------------------

    async def connect_to_port(self, port_name: str) -> None:
        """
        Connects to the given serial port and initializes the pump interface.

        Args:
            port_name (str): Serial port name (e.g., "COM4", "/dev/ttyUSB0")
        """
        try:
            async with anyio_serial.Serial(port=port_name, baudrate=IonPump.BAUD_RATE) as raw_port:
                self.serial = AnyIOSerialPort(
                    raw_port,
                    send_delimiter="\r",
                    receive_delimiter="\r",
                    codec="ascii"
                )
                self.connected_port = port_name
                print(f"Connected to {port_name}")
        except Exception as e:
            print(f"Failed to connect to {port_name}: {e}")

    def set_pump_address(self, address: int) -> None:
        """
        Updates the pump's address for multi-device support.

        Args:
            address (int): New address (0–99)

        Raises:
            ValueError: If address is outside valid range
        """
        if not (0 <= address <= 255):
            raise ValueError("Pump address must be between 0 and 99.")
        self._pump_address = address

    def get_pump_address(self) -> int:
        """
        Returns the currently configured pump address.

        Returns:
            int: Address value
        """
        return self._pump_address
