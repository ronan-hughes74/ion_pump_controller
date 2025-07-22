# --- Standard Library Imports ---
import sys
import asyncio
import ssl
import random  # (not currently used — can remove if unnecessary)

# --- Serial Port Discovery ---
import serial.tools.list_ports  # To populate available COM/serial ports

# --- PyQt5 GUI Imports ---
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton,
    QSpinBox, QWidget, QComboBox
)
from PyQt5.QtCore import QTimer

# --- Async Support for PyQt ---
from qasync import QEventLoop, asyncSlot

# --- Graphing ---
import pyqtgraph as pg

# --- Async IO & RPC ---
import anyio
from rockdove.rpc._clients import RemoteRPCClient
from rockdove.rpc._connections import RPCConnection


# =============================================================================
# 🖥️ GUI CLASS
# =============================================================================
class IonPumpGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ion Pump Controller")
        self.resize(600, 400)

        # --- Status and Control Widgets ---
        self.label = QLabel("Status: --")

        self.ping_button = QPushButton("Ping Device")
        self.ping_button.clicked.connect(self.ping_device)

        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(0, 10000)
        self.threshold_spinbox.setValue(500)

        self.apply_button = QPushButton("Apply Threshold")
        self.apply_button.clicked.connect(self.apply_threshold)

        self.extra_button_1 = QPushButton("Task 1")  # Placeholder for future feature
        self.extra_button_2 = QPushButton("Task 2")

        # --- Live Pressure Graph ---
        self.graph = pg.PlotWidget()
        self.graph.setTitle("Pressure Reading")
        self.graph.setLabel("left", "Pressure", units="Torr")
        self.graph.setLabel("bottom", "Time", units="s")

        self.pressure_data = []
        self.time_data = []
        self.t = 0
        self.plot = self.graph.plot(self.time_data, self.pressure_data, pen='y')

        # --- Serial Port Selector ---
        self.port_selector = QComboBox()
        self.refresh_ports()

        self.connect_button = QPushButton("Connect to Port")
        self.connect_button.clicked.connect(self.connect_to_selected_port)

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

        # --- State ---
        self.client = None

        # --- Timers ---
        self.refresh_ports()  # Populate port list on start

        self.port_refresh_timer = QTimer()
        self.port_refresh_timer.timeout.connect(self.refresh_ports)
        self.port_refresh_timer.start(5000)  # Refresh every 5 seconds

    # =========================================================================
    # 🔌 Serial Port Utilities
    # =========================================================================

    def refresh_ports(self):
        """
        Refresh the serial port list in the dropdown.
        """
        self.port_selector.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_selector.addItem(port.device)

    def connect_to_selected_port(self):
        """
        Tell the RPC client to connect to the currently selected serial port.
        """
        if self.client:
            selected_port = self.port_selector.currentText()
            asyncio.create_task(self.client.connect_to_port(selected_port))

    # =========================================================================
    # 🔗 RPC Client Setup
    # =========================================================================

    async def setup_client(self):
        """
        Establish a secure TLS connection to the RPC server and start polling.
        """
        async def stream_constructor():
            tls_context = RPCConnection.create_default_noauth_tls_context(
                ssl.Purpose.SERVER_AUTH
            )
            return await anyio.connect_tcp(
                "localhost", 1234,
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
        asyncio.create_task(self.poll_pressure())  # Begin live graph updates

    # =========================================================================
    # 📈 Pressure Polling & Graphing
    # =========================================================================

    async def poll_pressure(self):
        """
        Continuously poll pressure from the device and update the graph.
        """
        while True:
            try:
                pressure = await self.client.get_pressure()

                # Append new values
                self.time_data.append(self.t)
                self.pressure_data.append(pressure * 1e6)  # microTorr for graph

                # Trim to last 100 data points for performance
                if len(self.time_data) > 100:
                    self.time_data.pop(0)
                    self.pressure_data.pop(0)

                # Update the plot
                self.plot.setData(self.time_data, self.pressure_data)
                self.t += 1  # Advance time axis

            except Exception as e:
                self.label.setText(f"Error: {e}")

            await asyncio.sleep(1)

    # =========================================================================
    # 🎛️ User Actions
    # =========================================================================

    @asyncSlot()
    async def toggle_pump(self):
        """
        Example async button action to toggle pump state.
        """
        if self.client:
            await self.client.turn_on()

    def apply_threshold(self):
        """
        Send the selected threshold to the pump.
        """
        if self.client:
            threshold = self.threshold_spinbox.value()
            asyncio.create_task(self.client.set_pressure_threshold(threshold))

    def ping_device(self):
        """
        Trigger a ping call to the device (debug/testing).
        """
        print("Ping button clicked!")
        if self.client:
            try:
                response = asyncio.create_task(self.client.ping())
                print(f"Ping response: {response}")
            except Exception as e:
                print(f"Error during ping: {e}")


# =============================================================================
# 🚀 Entry Point
# =============================================================================

def main():
    """
    Start the PyQt event loop and GUI window.
    """
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = IonPumpGUI()
    window.show()
    loop.create_task(window.setup_client())  # Connect to RPC server

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
