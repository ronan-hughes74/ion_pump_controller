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


Data Flow:

main_window.py  <--RPC-->  rpc_namespace.py  <--->  ion_pump.py  <--->  Serial Device
    
1. Cloning Repository:

git clone https://github.com/yourusername/ion_pump_controller.git
cd ion_pump_controller

2. Installing Dependencies:

python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Running Server:

python -m pump_server.server

4. Launching GUI

python -m gui.main_window

5. Running Tests:

pytest tests/


Explanation of how the server works in more layman's terms (Because Ronan thinks this stuff is confusing):
server.py exposes IonPumpRPCNamespace, which gives access to pump control methods. Server.py starts the Rockdove server listening for incoming RPC calls on port 1234.
rpc_namespace.p defines which functions or objects are available to remote clients.
The client (main_window.py) connects to the RPC server and calls remote methods using rockdove.connect().
