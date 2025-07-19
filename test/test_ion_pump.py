import pytest
from pump_server.ion_pump import IonPump

class FakeSerial:
    async def query(self, cmd):
        if cmd == "PR?":
            return "1.23e-5"
        elif cmd == "STATUS?":
            return "ON"
        return "OK"

@pytest.mark.asyncio
async def test_get_pressure():
    pump = IonPump(FakeSerial())
    pressure = await pump.get_pressure()
    assert abs(pressure - 1.23e-5) < 1e-7

