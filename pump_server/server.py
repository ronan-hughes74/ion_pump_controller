# --- Standard Library Imports ---
from contextlib import asynccontextmanager  # For managing async setup/teardown
from typing import AsyncGenerator           # For typing the async generator

# --- Third-Party Imports ---
import anyio                               # Async concurrency framework
from rockdove.rpc import RPCServer         # Rockdove RPC server

# --- Project-Specific Imports ---
from pydux.control_support.anyio_extensions import Mutex  # Thread-safety for pump access
from .ion_pump import IonPump                             # Core device logic
from .rpc_namespace import IonPumpRPCNamespace            # RPC interface wrapper


@asynccontextmanager
async def get_namespace() -> AsyncGenerator[IonPumpRPCNamespace, None]:
    """
    Asynchronous context manager that initializes the IonPump and wraps it
    in a thread-safe RPC namespace. This yields the namespace to the server.

    Returns:
        AsyncGenerator[IonPumpRPCNamespace, None]: RPC namespace instance
    """
    pump = IonPump()                # Initialize ion pump hardware interface
    mutex = Mutex(pump)             # Wrap it with a Mutex to ensure safe async access
    namespace = IonPumpRPCNamespace(mutex)  # Pass mutex-wrapped pump to RPC interface
    yield namespace                 # Yield the fully prepared namespace


async def main():
    """
    Main async entry point. Initializes the RPC server and starts listening.
    """
    async with get_namespace() as namespace:        # Setup RPC namespace
        server = RPCServer(namespace)               # Create RPC server with the namespace
        print("✅ RPC Server listening on tcp://localhost:1234")
        await server.serve(1234, local_host="localhost")  # Start serving on port 1234


# Entry point for running as a script
if __name__ == "__main__":
    anyio.run(main, backend="asyncio")  # Launch main() using anyio with asyncio backend
