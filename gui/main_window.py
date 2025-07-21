import sys
import asyncio
import ssl
import random
import serial.tools.list_ports  # ⬅️ Add this to get available ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton,
    QSpinBox, QWidget, QHBoxLayout, QComboBox
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
        self.resize(600, 400)

        # --- Widgets ---
        self.label = QLabel("Status: --")
        self.ping_button = QPushButton("Ping Device")
        self.ping_button.clicked.connect(self.ping_device)

        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(0, 10000)
        self.threshold_spinbox.setValue(500)

        self.apply_button = QPushButton("Apply Threshold")
        self.apply_button.clicked.connect(self.apply_threshold)

        # --- Placeholder buttons for future tasks ---
        self.extra_button_1 = QPushButton("Task 1")
        self.extra_button_2 = QPushButton("Task 2")

        # --- Graph Setup ---
        self.graph = pg.PlotWidget()
        self.graph.setTitle("Pressure Reading")
        self.graph.setLabel("left", "Pressure", units="Torr")
        self.graph.setLabel("bottom", "Time", units="s")
        self.pressure_data = []
        self.time_data = []
        self.plot = self.graph.plot(self.time_data, self.pressure_data, pen='y')
        self.t = 0
        
        # --- Serial Port Selector ---
        self.port_selector = QComboBox()
        self.refresh_ports()

        self.connect_button = QPushButton("Connect to Port")
        self.connect_button.clicked.connect(self.connect_to_port)


        # --- Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.graph)
        layout.addWidget(self.ping_button)
        layout.addWidget(self.threshold_spinbox)
        layout.addWidget(self.apply_button)
        layout.addWidget(self.extra_button_1)
        layout.addWidget(self.extra_button_2)
        layout.addWidget(self.port_selector)
        layout.addWidget(self.connect_button)


        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.client = None


        # Refresh port list when app starts
        self.refresh_ports()

        # Auto-refresh every 5 seconds
        self.port_refresh_timer = QTimer()
        self.port_refresh_timer.timeout.connect(self.refresh_ports)
        self.port_refresh_timer.start(5000)
        
    def refresh_ports(self):
        """Populate the combo box with available serial ports."""
        self.port_selector.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_selector.addItem(port.device)

    def connect_to_selected_port(self):
        """Send the selected port to the RPC client to connect."""
        if self.client:
            selected_port = self.port_selector.currentText()
            asyncio.create_task(self.client.connect_to_port(selected_port))


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
                # Fetch the pressure
                pressure = await self.client.get_pressure()

                # Append to time and pressure data
                self.time_data.append(self.t)  # Time steps
                self.pressure_data.append(pressure * 1e6)  # Pressure in microtorr

                # Keep the last 100 data points for performance reasons
                if len(self.time_data) > 100:
                    self.time_data.pop(0)
                    self.pressure_data.pop(0)

                # Update the graph data
                self.plot.setData(self.time_data, self.pressure_data)

                # Increment the time counter for the x-axis
                self.t += 1

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

    def ping_device(self):
        print("Ping button clicked!")
        if self.client:
            try:
                # Assuming a ping method exists on the client
                response = asyncio.create_task(self.client.ping())
                print(f"Ping response: {response}")
            except Exception as e:
                print(f"Error during ping: {e}")

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
