# --- Project-Specific Imports ---
from pydux.control_support.anyio_extensions import Mutex  # Thread-safe access wrapper
from .ion_pump import IonPump                             # Ion pump device interface

# --- Standard Library Imports ---
from contextlib import asynccontextmanager                # For async context management


class IonPumpRPCNamespace:
    """
    RPC namespace for exposing IonPump functionality over Rockdove.
    This class wraps an IonPump instance with a Mutex to safely support
    concurrent access from multiple clients.
    """

    def __init__(self, mutex: Mutex[IonPump]):
        """
        Initialize the RPC namespace with a mutex-protected IonPump instance.
        
        Args:
            mutex (Mutex[IonPump]): A concurrency-safe wrapper around the pump.
        """
        self._mutex = mutex

    @asynccontextmanager
    async def make_context(self):
        """
        Optional server-wide setup hook for Rockdove.
        Useful for initializing shared resources or global state.
        Currently a no-op.
        """
        yield

    @asynccontextmanager
    async def make_client_context(self, client):
        """
        Optional per-client setup hook for Rockdove.
        Can be used to prepare resources or authentication for individual clients.
        Currently a no-op.
        
        Args:
            client: Metadata or identifier for the connected client.
        """
        yield

    async def get_pressure(self) -> float:
        """
        RPC-exposed method to get the current pressure from the ion pump.

        Returns:
            float: The pressure reading.
        """
        async with self._mutex.guard() as pump:
            return await pump.get_pressure()

    async def connect_to_port(self, port_name: str) -> str:
        """
        RPC-exposed method to connect the ion pump to a specified serial port.

        Args:
            port_name (str): The name/path of the serial port (e.g., COM3, /dev/ttyUSB0)

        Returns:
            str: Confirmation message after connection.
        """
        async with self._mutex as pump:
            await pump.connect_to_port(port_name)
            return f"Connected to {port_name}"
