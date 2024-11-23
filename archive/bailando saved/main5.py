from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QMouseEvent, QKeyEvent
from PySide6.QtCore import QTimer, Qt, QPoint
import os
import sys

# Path to save the window position
POSITION_FILE = "pos.txt"

# Set up the main application window
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Bailando")
window.setFixedSize(450, 300)
window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Frameless and stays on top initially
window.setAttribute(Qt.WA_TranslucentBackground)  # Make window background transparent

# Load previous window position if available
def load_position():
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, "r") as file:
            x, y = map(int, file.read().split(","))
            return QPoint(x, y)
    # Default to center of screen if no previous position
    screen_center = app.primaryScreen().availableGeometry().center()
    return QPoint(screen_center.x() - window.width() // 2, screen_center.y() - window.height() // 2)

# Save the current window position to file
def save_position():
    with open(POSITION_FILE, "w") as file:
        file.write(f"{window.x()},{window.y()}")

# Set initial position of the window
initial_position = load_position()
window.move(initial_position)

# Layout and label for displaying images
layout = QVBoxLayout()
label = QLabel()
label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
label.setAttribute(Qt.WA_TranslucentBackground)
label.setStyleSheet("background: transparent;")
layout.addWidget(label)
window.setLayout(layout)

# Folder containing the images in order
image_folder = "/img"
image_files = sorted(
    [f for f in os.listdir(image_folder) if f.lower().endswith(('.png'))]
)

# Load all images and store them in a list
images = [QPixmap(os.path.join(image_folder, img)) for img in image_files]

# Initialize index and display the first image
image_index = 0
label.setPixmap(images[image_index])

# Function to update the image every 30 milliseconds
def update_image():
    global image_index
    image_index = (image_index + 1) % len(images)  # Cycle through images
    label.setPixmap(images[image_index])

# Set up a timer to update the image
timer = QTimer()
timer.timeout.connect(update_image)
timer.start(30)  # Update every 30 milliseconds

# Variables to track dragging and locking state
dragging = False
locked = False
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
        save_position()  # Save position when user releases the window

# Function to toggle the locked state when "Home" is pressed
def keyPressEvent(event: QKeyEvent):
    global locked
    if event.key() == Qt.Key_Home:
        locked = not locked
        if locked:
            window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            window.setWindowFlags(window.windowFlags() & ~Qt.WindowStaysOnTopHint)
        window.show()  # Refresh window flags

# Connect mouse events and key event to the window
window.mousePressEvent = mousePressEvent
window.mouseMoveEvent = mouseMoveEvent
window.mouseReleaseEvent = mouseReleaseEvent
window.keyPressEvent = keyPressEvent

# Display the window and start the application
window.show()
sys.exit(app.exec())
