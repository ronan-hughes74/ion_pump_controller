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

