from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QDialog, QPushButton, QSystemTrayIcon, QSlider
from PySide6.QtGui import QPixmap, QMouseEvent, QKeyEvent, QIcon, QKeySequence, QCursor
from PySide6.QtCore import QTimer, Qt, QPoint, QThread, Signal
import os
import sys
import json
import threading
import time
import win32gui
import win32con

# Determine the base path for the executable
base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))

# Path to save the settings in JSON format
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), "bailando_settings.json")
DEFAULT_SETTINGS = {
    "position": {
        "x": 500,
        "y": 500
    },
    "hotkey": "End",
    "opacity": 255
}


def keep_window_on_top():
    def monitor_window():
        while True:
            hwnd = win32gui.FindWindow(None, window.windowTitle())
            if hwnd:
                # Ensure the window is always on top
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            time.sleep(0.01)  # Check every 10ms to ensure it stays on top

    # Run the monitoring function in a separate thread to avoid blocking the main UI thread
    thread = threading.Thread(target=monitor_window, daemon=True)
    thread.start()

# Function to load settings from the JSON file
def load_data():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as file:
                data = json.load(file)
                x = data.get('position', {}).get('x', DEFAULT_SETTINGS['position']['x'])
                y = data.get('position', {}).get('y', DEFAULT_SETTINGS['position']['y'])
                hotkey = data.get('hotkey', DEFAULT_SETTINGS['hotkey'])
                transparency = data.get('opacity', DEFAULT_SETTINGS['opacity'])
                print("Loaded settings from JSON:")
                print(f"Position: ({x}, {y}), Hotkey: {hotkey}, Opacity: {transparency}")
                return QPoint(x, y), hotkey, transparency
        except json.JSONDecodeError:
            # Remove corrupted file and reset to default settings
            print("Error loading JSON. Resetting to default settings.")
            os.remove(SETTINGS_FILE)
            save_data(
                position=QPoint(DEFAULT_SETTINGS['position']['x'], DEFAULT_SETTINGS['position']['y']),
                hotkey=DEFAULT_SETTINGS['hotkey'],
                transparency=DEFAULT_SETTINGS['opacity']
            )
            return QPoint(DEFAULT_SETTINGS['position']['x'], DEFAULT_SETTINGS['position']['y']), \
                   DEFAULT_SETTINGS['hotkey'], DEFAULT_SETTINGS['opacity']
    else:
        print("No settings file found, loading default settings.")
        return QPoint(DEFAULT_SETTINGS['position']['x'], DEFAULT_SETTINGS['position']['y']), \
               DEFAULT_SETTINGS['hotkey'], DEFAULT_SETTINGS['opacity']



# Function to save settings to the JSON file
def save_data(position=None, hotkey=None, transparency=None):
    settings = {}
    if position:
        settings['position'] = {'x': position.x(), 'y': position.y()}
    if hotkey:
        settings['hotkey'] = hotkey
    if transparency is not None:
        settings['opacity'] = transparency

    # Load existing settings if any
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            existing_data = json.load(file)
            settings = {**existing_data, **settings}

    # Save the updated settings back to the file
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)

    # Debug print statement
    print("Saved settings to JSON:")
    print(json.dumps(settings, indent=4))

# Thread for loading images
class ImageLoaderThread(QThread):
    images_loaded = Signal(list)

    def run(self):
        image_folder = os.path.join(base_path, "img")
        image_files = sorted(f for f in os.listdir(image_folder) if f.lower().endswith('.png'))
        self.images_loaded.emit(image_files)

# Set up the main application window
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Bailando")
window.setFixedSize(450, 300)
window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
window.setAttribute(Qt.WA_TranslucentBackground)
keep_window_on_top()

if hasattr(sys, '_MEIPASS'):
    exe_icon_path = os.path.join(base_path, "icon.ico")
    window.setWindowIcon(QIcon(exe_icon_path))

# Load data and set initial position of the window
position, hotkey, transparency = load_data()
window.move(position)
window.setWindowOpacity(transparency / 255)  # Set the initial opacity

def update_hotkey():
    global hotkey
    position, hotkey_text, transparency = load_data()
    try:
        hotkey = getattr(Qt, f"Key_{hotkey_text.capitalize()}")
    except AttributeError:
        hotkey = Qt.Key_End

# Timer to check for changes in settings.json
settings_check_timer = QTimer()
settings_check_timer.setInterval(1000)  # Check every second
settings_check_timer.timeout.connect(update_hotkey)
settings_check_timer.start()

# Layout and label for displaying images
layout = QVBoxLayout()
label = QLabel()
label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
label.setAttribute(Qt.WA_TranslucentBackground)
label.setStyleSheet("background: transparent;")
layout.addWidget(label)
window.setLayout(layout)

# Initialize image index and images list
image_index = 0
image_files = []
current_image = None

# Update image function
def update_image():
    global image_index, current_image
    if image_files:
        next_image_path = os.path.join(base_path, "img", image_files[image_index])
        current_image = QPixmap(next_image_path)
        label.setPixmap(current_image)
        image_index = (image_index + 1) % len(image_files)

# Set up a timer to update the image
image_update_timer = QTimer()
image_update_timer.timeout.connect(update_image)
image_update_timer.start(30)

# Load images using threading
def on_images_loaded(images_list):
    global image_files
    image_files = images_list
    update_image()

image_loader_thread = ImageLoaderThread()
image_loader_thread.images_loaded.connect(on_images_loaded)
image_loader_thread.start()

# Create a system tray icon
tray_icon = QSystemTrayIcon(QIcon(os.path.join(base_path, "icon.ico")), parent=app)
tray_icon.setVisible(False)

# Variables for dragging and locking state
dragging = False
locked = True
mouse_offset = QPoint()

# Override mouse events for dragging the window
def mousePressEvent(event: QMouseEvent):
    global dragging, mouse_offset
    if event.button() == Qt.LeftButton and not locked:
        dragging = True
        mouse_offset = QCursor.pos() - window.frameGeometry().topLeft()  # Calculate offset relative to window

def mouseMoveEvent(event: QMouseEvent):
    global dragging
    if dragging and not locked:
        window.move(QCursor.pos() - mouse_offset)  # Move window using cursor position

def mouseReleaseEvent(event: QMouseEvent):
    global dragging
    if event.button() == Qt.LeftButton:
        dragging = False
        save_data(position=window.pos(), transparency=int(window.windowOpacity() * 255))

class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration")
        self.setFixedSize(300, 200)

        self.layout = QVBoxLayout()
        self.hotkey_label = QLabel("Press any key to set as hotkey")
        self.layout.addWidget(self.hotkey_label)

        # Slider for transparency
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(0, 255)
        self.transparency_slider.setValue(transparency)  # Set the initial value from JSON
        self.transparency_slider.valueChanged.connect(self.change_transparency)
        self.layout.addWidget(QLabel("Adjust Transparency:"))
        self.layout.addWidget(self.transparency_slider)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(save_button)

        # Reset button to restore default settings
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_settings)
        self.layout.addWidget(reset_button)

        self.setLayout(self.layout)
        self.current_key = None

    def keyPressEvent(self, event: QKeyEvent):
        # Check for the valid keys
        if event.key() in [Qt.Key_Escape, Qt.Key_Home]:
            # Ignore Escape and Home keys for hotkey assignment
            return
        
        self.current_key = event.key()
        key_name = QKeySequence(self.current_key).toString()

        # Check if the key is valid and set the hotkey label
        if self.current_key != Qt.Key_unknown:
            self.hotkey_label.setText(f"Current hotkey: {key_name.upper()}")
        else:
            self.hotkey_label.setText("Invalid key! Please try again.")

    def save_settings(self):
        # Save the hotkey and transparency values
        if self.current_key:
            if self.current_key == Qt.Key_Home:
                self.hotkey_label.setText("Home key cannot be set as hotkey!")
                return  # Prevent saving the Home key
            hotkey_text = QKeySequence(self.current_key).toString().upper()
            save_data(hotkey=hotkey_text)

        # Save the current transparency value
        transparency_value = self.transparency_slider.value()
        save_data(transparency=transparency_value)
        window.setWindowOpacity(transparency_value / 255)  # Update window opacity
        
        self.accept()

    def change_transparency(self, value):
        window.setWindowOpacity(value / 255)  # Update window opacity live as slider moves

    def reset_settings(self):
        # Reset to default settings
        self.current_key = getattr(Qt, f"Key_{DEFAULT_SETTINGS['hotkey']}")
        self.hotkey_label.setText(f"Current hotkey: {DEFAULT_SETTINGS['hotkey'].upper()}")
        
        self.transparency_slider.setValue(DEFAULT_SETTINGS['opacity'])
        window.setWindowOpacity(DEFAULT_SETTINGS['opacity'] / 255)

        # Save default settings to the settings file
        save_data(
            position=QPoint(DEFAULT_SETTINGS['position']['x'], DEFAULT_SETTINGS['position']['y']),
            hotkey=DEFAULT_SETTINGS['hotkey'],
            transparency=DEFAULT_SETTINGS['opacity']
        )

# Function to toggle the locked state or open config dialog based on the hotkey
def keyPressEvent(event: QKeyEvent):
    global locked
    if event.key() == hotkey:
        locked = not locked
        window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | (Qt.Tool if locked else 0))
        window.show()
        tray_icon.setVisible(locked)

    elif event.key() == Qt.Key_Home:
        config_dialog = ConfigDialog()
        config_dialog.exec()

# Connect mouse events and key event to the window
window.mousePressEvent = mousePressEvent
window.mouseMoveEvent = mouseMoveEvent
window.mouseReleaseEvent = mouseReleaseEvent
window.keyPressEvent = keyPressEvent

# Override the closeEvent of the window
def closeEvent(event):
    # Save data when the window is closed
    save_data(position=window.pos(), transparency=int(window.windowOpacity() * 255))

    # Print position and transparency for debugging
    print(f"Closing window, saving position: {window.pos()}, transparency: {int(window.windowOpacity() * 255)}")
    print("Settings saved on close event.")

    event.accept()
    app.quit()

window.closeEvent = closeEvent  # Set the custom close event

# Show the window
window.show()
sys.exit(app.exec())
