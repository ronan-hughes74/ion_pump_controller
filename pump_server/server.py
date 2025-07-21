from contextlib import asynccontextmanager
from typing import AsyncGenerator


import anyio
from rockdove.rpc import RPCServer

from pydux.control_support.anyio_extensions import Mutex
from .ion_pump import IonPump
from .rpc_namespace import IonPumpRPCNamespace


@asynccontextmanager
async def get_namespace() -> AsyncGenerator[IonPumpRPCNamespace, None]:
    """
    Yields an IonPumpRPCNamespace instance for use with the Rockdove RPCServer.
    """
    pump = IonPump()
    mutex = Mutex(pump)
    namespace = IonPumpRPCNamespace(mutex)
    yield namespace

async def main():
    async with get_namespace() as namespace:
        server = RPCServer(namespace)
        print("✅ RPC Server listening on tcp://localhost:1234")
        await server.serve(1234, local_host="localhost")



if __name__ == "__main__":
    anyio.run(main, backend="asyncio")
