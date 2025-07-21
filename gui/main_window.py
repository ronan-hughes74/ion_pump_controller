import sys
import asyncio
import ssl
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton,
    QSpinBox, QWidget, QHBoxLayout
)
from PyQt5.QtCore import QTimer
from qasync import QEventLoop, asyncSlot
import pyqtgraph as pg
import anyio
from rockdove.rpc._clients import RemoteRPCClient
from rockdove.rpc._connections import RPCConnection


class IonPumpGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ion Pump Controller")

        # --- Widgets ---
        self.label = QLabel("Pressure: --")

        self.ping_button = QPushButton("Ping Device")
        self.ping_button.clicked.connect(self.ping_device)

        self.on_button = QPushButton("Turn ON Pump")
        self.on_button.clicked.connect(self.toggle_pump)

        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(0, 10000)
        self.threshold_spinbox.setValue(500)

        self.apply_button = QPushButton("Apply Threshold")
        self.apply_button.clicked.connect(self.apply_threshold)

        # --- Placeholder buttons for future tasks ---
        self.extra_button_1 = QPushButton("Task 1")
        self.extra_button_2 = QPushButton("Task 2")

        # --- Graph setup ---
        self.graph = pg.PlotWidget()
        self.graph.setYRange(0, 100)
        self.x_data = list(range(100))
        self.y_data = [0] * 100
        self.plot = self.graph.plot(self.x_data, self.y_data, pen='g')

        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(self.update_graph)
        self.graph_timer.start(500)  # Update graph every 500 ms

        # --- Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.graph)
        layout.addWidget(self.ping_button)
        layout.addWidget(self.on_button)
        layout.addWidget(self.threshold_spinbox)
        layout.addWidget(self.apply_button)
        layout.addWidget(self.extra_button_1)
        layout.addWidget(self.extra_button_2)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.client = None

    async def setup_client(self):
        async def stream_constructor():
            tls_context = RPCConnection.create_default_noauth_tls_context(ssl.Purpose.SERVER_AUTH)
            return await anyio.connect_tcp(
                "localhost",
                1234,
                tls=True,
                ssl_context=tls_context,
                tls_hostname=None
            )

        tls_stream = await stream_constructor()

        connection = await RPCConnection(
            tls_stream,
            namespace=RemoteRPCClient,
            PeerDisconnectedError=RemoteRPCClient.PeerDisconnectedError,
        ).__aenter__()

        self.client = connection.namespace
        asyncio.create_task(self.poll_pressure())

    async def poll_pressure(self):
        while True:
            try:
                pressure = await self.client.get_pressure()
                self.label.setText(f"Pressure: {pressure:.2e} Torr")
                self.y_data = self.y_data[1:] + [pressure * 1e6]  # rescaled for graph
                self.plot.setData(self.x_data, self.y_data)
            except Exception as e:
                self.label.setText(f"Error: {e}")
            await asyncio.sleep(1)

    @asyncSlot()
    async def toggle_pump(self):
        if self.client:
            await self.client.turn_on()

    def apply_threshold(self):
        if self.client:
            threshold = self.threshold_spinbox.value()
            asyncio.create_task(self.client.set_pressure_threshold(threshold))

    def update_graph(self):
        # Graph updates happen in poll_pressure (for pressure),
        # but this is here if you want simulated data instead:
        pass

    def ping_device(self):
        print("Ping button clicked!")
        # You can later replace this with: asyncio.create_task(self.client.ping())


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
