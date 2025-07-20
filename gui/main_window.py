from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
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
        
        # Create a QSpinBox to select the pressure threshold
        self.threshold_spinbox = QSpinBox(self)
        self.threshold_spinbox.setRange(0, 10000)  # Set range for the threshold
        self.threshold_spinbox.setValue(500)  # Set default value
        layout.addWidget(self.threshold_spinbox)

        # Button to apply the threshold
        self.apply_button = QPushButton("Apply Threshold", self)
        self.apply_button.clicked.connect(self.apply_threshold)
        layout.addWidget(self.apply_button)


        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.client = None
        asyncio.create_task(self.setup_client())

    async def setup_client(self):
        self.client = await rockdove.client.connect("ws://localhost:5000")
        asyncio.create_task(self.poll_pressure())

    async def poll_pressure(self):
        while True:
            pressure = await self.client.ion_pump.get_pressure()
            self.label.setText(f"Pressure: {pressure:.2e} Torr")
            await asyncio.sleep(1)
            
    def apply_pump_address(self):
        threshold = self.trheshold_spinbox.value()
        self.ion_pump.set_pressure_threshold(threshold)
    
    @asyncSlot()
    async def toggle_pump(self):
        await self.client.ion_pump.turn_on()

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

