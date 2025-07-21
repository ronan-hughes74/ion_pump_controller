from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QSpinBox
import sys
import asyncio
import ssl
from qasync import QEventLoop, asyncSlot
import anyio
from rockdove.rpc._clients import RemoteRPCClient
from rockdove.rpc._connections import RPCConnection  # Needed for direct connection
import anyio.streams.tls

class IonPumpGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize UI components
        self.label = QLabel("Pressure: --")
        self.button = QPushButton("Turn ON Pump")
        self.button.clicked.connect(self.toggle_pump)

        self.threshold_spinbox = QSpinBox(self)
        self.threshold_spinbox.setRange(0, 10000)
        self.threshold_spinbox.setValue(500)

        self.apply_button = QPushButton("Apply Threshold", self)
        self.apply_button.clicked.connect(self.apply_threshold)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.threshold_spinbox)
        layout.addWidget(self.apply_button)
        self.setLayout(layout)

        self.client = None

    async def setup_client(self):
        """
        Set up the connection to the remote server using RemoteRPCClient.
        """
        async def stream_constructor():
            tls_context = RPCConnection.create_default_noauth_tls_context(ssl.Purpose.SERVER_AUTH)
            return await anyio.connect_tcp(
                "localhost",
                1234,
                tls=True,
                ssl_context=tls_context,
                tls_hostname=None  # Assuming no cert validation
            )

        tls_stream = await stream_constructor()

        connection = await RPCConnection(
            tls_stream,
            PeerDisconnectedError=RemoteRPCClient.PeerDisconnectedError,
        ).__aenter__()  # Manual context enter because we're not using `async with`

        self.client = RemoteRPCClient(connection)

        # Start pressure polling
        asyncio.create_task(self.poll_pressure())

    async def poll_pressure(self):
        while True:
            try:
                pressure = await self.client.get_pressure()
                self.label.setText(f"Pressure: {pressure:.2e} Torr")
            except Exception as e:
                self.label.setText(f"Error: {e}")
            await asyncio.sleep(1)

    def apply_threshold(self):
        threshold = self.threshold_spinbox.value()
        asyncio.create_task(self.client.set_pressure_threshold(threshold))

    @asyncSlot()
    async def toggle_pump(self):
        await self.client.turn_on()


def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = IonPumpGUI()
    window.show()

    loop.create_task(window.setup_client())

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
