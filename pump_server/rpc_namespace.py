from pydux.control_support.anyio_extensions import Mutex
from .ion_pump import IonPump

class IonPumpRPCNamespace:
    def __init__(self, mutex: Mutex[IonPump]):
        self._mutex = mutex

    async def get_pressure(self) -> float:
        async with self._mutex.guard() as pump:
            return await pump.read_pressure()

    async def set_pressure_threshold(self, threshold: int) -> None:
        async with self._mutex.guard() as pump:
            pump.set_threshold(threshold)

    async def turn_on(self) -> None:
        async with self._mutex.guard() as pump:
            await pump.turn_on()

    async def turn_off(self) -> None:
        async with self._mutex.guard() as pump:
            await pump.turn_off()
