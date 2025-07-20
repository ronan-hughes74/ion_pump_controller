from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox
from PyQt5.QtCore import QTimer
import sys
import asyncio
from qasync import QEventLoop, asyncSlot
import rockdove.client

class IonPumpGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel("Pressure: --")
        self.button = QPushButton("Turn ON Pump")
        self.button.clicked.connect(self.toggle_pump)

        self.threshold_spinbox = QSpinBox(self)
        self.threshold_spinbox.setRange(0, 10000)
        self.threshold_spinbox.setValue(500)

        self.apply_button = QPushButton("Apply Threshold", self)
        self.apply_button.clicked.connect(self.apply_threshold)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.threshold_spinbox)
        self.layout.addWidget(self.apply_button)
        self.setLayout(self.layout)

        self.client = None

        # ✅ Defer async client setup until event loop is running
        QTimer.singleShot(0, self.setup_client)

    @asyncSlot()
    async def setup_client(self):
        self.client = await rockdove.client.connect("ws://localhost:5000")
        asyncio.create_task(self.poll_pressure())

    async def poll_pressure(self):
        while True:
            pressure = await self.client.ion_pump.get_pressure()
            self.label.setText(f"Pressure: {pressure:.2e} Torr")
            await asyncio.sleep(1)

    def apply_threshold(self):
        threshold = self.threshold_spinbox.value()
        self.client.ion_pump.set_pressure_threshold(threshold)
        print(f"Threshold applied: {threshold}")

    @asyncSlot()
    async def toggle_pump(self):
        await self.client.ion_pump.turn_on()
        print("Pump turned on")

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = IonPumpGUI()
    window.show()

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()

