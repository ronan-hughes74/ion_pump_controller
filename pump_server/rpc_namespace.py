from rockdove.rpc import RPCNamespace
from pydux.control_support.anyio_extensions import Mutex
from pydux.control_support.rpc_utils import add_proxies_for_device
from .ion_pump import IonPump

@add_proxies_for_device(IonPump)
class IonPumpRPCNamespace(RPCNamespace):
    def __init__(self, device_mutex: Mutex[IonPump]) -> None:
        super().__init__()
        self._device_mutex = device_mutex

