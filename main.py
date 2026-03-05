import sys
import keyboard
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

from model import CaptureModel
from controller import CaptureController

class HotkeySignaler(QObject):
    """
    Used to safely trigger GUI updates from the keyboard hook's background thread.
    """
    capture_requested = pyqtSignal()

def main():
    app = QApplication(sys.argv)
    
    # Keep the application alive even when the capture window is closed
    app.setQuitOnLastWindowClosed(False)
    
    # Initialize MVC components
    model = CaptureModel()
    controller = CaptureController(model)
    
    # Set up cross-thread signaling
    signaler = HotkeySignaler()
    # Connect the signal to the controller's capture method safely on the main thread
    signaler.capture_requested.connect(controller.start_capture)
    
    # Register global hotkey
    keyboard.add_hotkey('ctrl+alt+a', signaler.capture_requested.emit)
    
    print("Easy Cap is running in the background.")
    print("Press 'Ctrl+Alt+A' anytime to start a capture.")
    print("Note: Keep this console open. Stop the script to exit.")
    
    # Start the Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
