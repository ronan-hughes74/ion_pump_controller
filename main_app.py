# main_app.py

import multiprocessing
import sys
import anyio

"""
How to use:
1. Place this in your project root, alongside your gui/ and pump_server/ folders.
2. Run it:
    python main_app.py
3. When ready to bundle:
    pyinstaller --onefile --windowed main_app.py



"""
# Import your server and GUI main functions
from pump_server.server import main as run_server
from gui.main_window import main as run_gui  # Update the import if needed

def start_server():
    """
    Starts the async RPC server in a separate process using AnyIO with asyncio backend.
    """
    anyio.run(run_server, backend="asyncio")

def start_gui():
    """
    Starts the GUI. This must run in the main process because of Qt/PyQt.
    """
    run_gui()

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Important for PyInstaller on Windows

    # Start server in a background process
    server_process = multiprocessing.Process(target=start_server)
    server_process.start()

    try:
        # Start GUI in the main process
        start_gui()
    finally:
        # Ensure server shuts down when GUI exits
        if server_process.is_alive():
            server_process.terminate()
            server_process.join()
