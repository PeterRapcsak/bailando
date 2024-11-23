from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QDialog, QPushButton, QSystemTrayIcon, QMenu
from PySide6.QtGui import QPixmap, QMouseEvent, QKeyEvent, QIcon, QKeySequence
from PySide6.QtCore import QTimer, Qt, QPoint, QThread, Signal
import csv
import os
import sys

# Determine the base path for the executable
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

# Path to save the data
DATA_FILE = os.path.join(base_path, "data.csv")

# Default settings
DEFAULT_HOTKEY = "End"

# Function to load data from CSV file
def load_data():
    data = {"position": None, "hotkey": DEFAULT_HOTKEY}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == "position":
                    x, y = map(int, row[1:])
                    data["position"] = QPoint(x, y)
                elif row[0] == "hotkey":
                    data["hotkey"] = row[1]

    if not data["position"]:
        screen_center = app.primaryScreen().availableGeometry().center()
        data["position"] = QPoint(screen_center.x() - window.width() // 2,
                                  screen_center.y() - window.height() // 2)
    return data

# Function to save data to CSV file
def save_data(position=None, hotkey=None):
    data = load_data()
    if position:
        data["position"] = position
    if hotkey:
        data["hotkey"] = hotkey

    with open(DATA_FILE, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["position", data["position"].x(), data["position"].y()])
        writer.writerow(["hotkey", data["hotkey"]])

# Thread for loading images
class ImageLoaderThread(QThread):
    images_loaded = Signal(list)

    def run(self):
        # Load image file names
        image_folder = os.path.join(base_path, "img")
        image_files = sorted([f for f in os.listdir(image_folder) if f.lower().endswith('.png')])
        self.images_loaded.emit(image_files)  # Emit only filenames

# Set up the main application window
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Bailando")
window.setFixedSize(450, 300)
window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Keep the window frameless and on top
window.setAttribute(Qt.WA_TranslucentBackground)

if hasattr(sys, '_MEIPASS'):
    exe_icon_path = os.path.join(base_path, "icon.ico")
    window.setWindowIcon(QIcon(exe_icon_path))

# Load data and set initial position of the window
data = load_data()
window.move(data["position"])

try:
    hotkey = getattr(Qt, f"Key_{data['hotkey'].capitalize()}")
except AttributeError:
    hotkey = int(data['hotkey'])

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
image_files = []  # Store only filenames
current_image = None  # To keep the current image in memory

# Update image function
def update_image():
    global image_index, current_image
    if image_files:  # Check if images are loaded
        # Load the next image
        next_image_path = os.path.join(base_path, "img", image_files[image_index])
        current_image = QPixmap(next_image_path)
        label.setPixmap(current_image)

        # Release the previous image if it exists
        if image_index > 0:
            del current_image  # Help with garbage collection

        image_index = (image_index + 1) % len(image_files)

# Set up a timer to update the image
timer = QTimer()
timer.timeout.connect(update_image)
timer.start(30)

# Load images using threading
def on_images_loaded(images_list):
    global image_files
    image_files = images_list
    update_image()  # Show the first image once loaded

image_loader_thread = ImageLoaderThread()
image_loader_thread.images_loaded.connect(on_images_loaded)
image_loader_thread.start()  # Start loading images in a separate thread

# Create a system tray icon
tray_icon = QSystemTrayIcon(QIcon(os.path.join(base_path, "icon.ico")), parent=app)
tray_icon.setVisible(False)  # Initially hidden

# Variables for dragging and locking state
dragging = False
locked = True
mouse_offset = QPoint()

# Override mouse events for dragging the window
def mousePressEvent(event: QMouseEvent):
    global dragging, mouse_offset
    if event.button() == Qt.LeftButton and not locked:
        dragging = True
        mouse_offset = event.pos()

def mouseMoveEvent(event: QMouseEvent):
    global dragging
    if dragging and not locked:
        new_pos = window.pos() + event.pos() - mouse_offset
        window.move(new_pos)

def mouseReleaseEvent(event: QMouseEvent):
    global dragging
    if event.button() == Qt.LeftButton:
        dragging = False
        save_data(position=window.pos())

# Configuration dialog for setting the hotkey
class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration")
        self.setFixedSize(300, 100)
        
        self.layout = QVBoxLayout()
        
        self.hotkey_label = QLabel("Press any key to set as hotkey")
        self.layout.addWidget(self.hotkey_label)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_hotkey)
        self.layout.addWidget(save_button)

        self.setLayout(self.layout)
        self.current_key = None

    def keyPressEvent(self, event: QKeyEvent):
        self.current_key = event.key()
        key_name = QKeySequence(self.current_key).toString()
        self.hotkey_label.setText(f"Current hotkey: {key_name.upper()}")

    def save_hotkey(self):
        if self.current_key:
            hotkey_text = QKeySequence(self.current_key).toString().upper()
            save_data(hotkey=hotkey_text)  # Save the hotkey in the CSV file
            global hotkey
            hotkey = self.current_key  # Update the global hotkey variable
        self.accept()  # Close the dialog

# Function to toggle the locked state or open config dialog based on the hotkey
def keyPressEvent(event: QKeyEvent):
    global locked
    if event.key() == hotkey:
        locked = not locked
        if locked:
            # Hide from taskbar by removing the Window flag
            window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            window.show()  # Refresh window flags
            tray_icon.setVisible(True)  # Optionally show tray icon
        else:
            # Restore taskbar visibility
            window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            window.show()  # Refresh window flags
            tray_icon.setVisible(False)  # Hide tray icon if not locked
    elif event.key() == Qt.Key_Home:
        config_dialog = ConfigDialog()
        config_dialog.exec()

# Connect mouse events and key event to the window
window.mousePressEvent = mousePressEvent
window.mouseMoveEvent = mouseMoveEvent
window.mouseReleaseEvent = mouseReleaseEvent
window.keyPressEvent = keyPressEvent

# Display the window and start the application
window.show()
sys.exit(app.exec())
