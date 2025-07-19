## Project Structure:
ion_pump_controller/
├── pump_server/
│   ├── __init__.py
│   ├── ion_pump.py          # Device logic
│   ├── rpc_namespace.py     # RPC namespace
│   └── server.py            # rockdove entry point
├── gui/
│   ├── __init__.py
│   └── main_window.py       # PyQt5 or Tkinter GUI
├── tests/
│   └── test_ion_pump.py     # Unit tests (with mocked serial)
├── requirements.txt
└── README.md
