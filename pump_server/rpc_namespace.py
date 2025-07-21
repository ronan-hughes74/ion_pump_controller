from pydux.control_support.anyio_extensions import Mutex
from .ion_pump import IonPump
from contextlib import asynccontextmanager


class IonPumpRPCNamespace:
    def __init__(self, mutex: Mutex[IonPump]):
        self._mutex = mutex

    @asynccontextmanager
    async def make_context(self):
        # Server-wide setup (e.g., shared state)
        yield

    @asynccontextmanager
    async def make_client_context(self, client):
        # Per-client setup (if needed); can also be a no-op
        yield

    async def get_pressure(self) -> float:
        async with self._mutex.guard() as pump:
            return await pump.get_pressure()
            
    async def connect_to_port(self, port_name: str) -> str:
        async with self._mutex as pump:
            await pump.connect_to_port(port_name)
            return f"Connected to {port_name}"

    """async def set_pressure_threshold(self, threshold: int) -> None:
        async with self._mutex.guard() as pump:
            pump.set_threshold(threshold)"""

 """  async def turn_on(self) -> None:
        async with self._mutex.guard() as pump:
            await pump.turn_on()

    async def turn_off(self) -> None:
        async with self._mutex.guard() as pump:
            await pump.turn_off()
"""