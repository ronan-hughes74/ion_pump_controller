from contextlib import asynccontextmanager
from typing import AsyncGenerator

import anyio_serial
from pydux.control_support.anyio_extensions import Guard, Mutex
from pydux.control_support.pyserial_extensions import AnyIOSerialPort
from .ion_pump import IonPump
from .rpc_namespace import IonPumpRPCNamespace

@asynccontextmanager
async def main(*, serial_port: str) -> AsyncGenerator[IonPumpRPCNamespace, None]:
    async with anyio_serial.Serial(port=serial_port, baudrate=IonPump.BAUD_RATE) as raw_port:
        port = AnyIOSerialPort(Guard(raw_port), send_delimiter="\r", receive_delimiter="\r", codec="ascii")
        yield IonPumpRPCNamespace(Mutex(IonPump(port)))

