import sys
import time
import threading
import win32gui
import win32con
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Always On Top Window")
        self.setGeometry(100, 100, 300, 200)  # Set window size and position

        # Set the window to be always on top
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        # Make the window transparent (optional, if you want a blank window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Start a background thread to keep the window on top
        self.keep_window_on_top()

    def keep_window_on_top(self):
        def monitor_window():
            while True:
                hwnd = win32gui.FindWindow(None, self.windowTitle())
                if hwnd:
                    # Ensure the window is always on top
                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                time.sleep(0.01)  # Check every 100ms

        # Run the monitoring function in a separate thread to avoid blocking the main UI thread
        thread = threading.Thread(target=monitor_window, daemon=True)
        thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
