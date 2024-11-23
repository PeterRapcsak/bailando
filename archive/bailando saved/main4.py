from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QPalette, QColor, QMouseEvent, QKeyEvent
from PySide6.QtCore import QTimer, Qt, QPoint
import os
import sys

# Set up the main application window
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Image Animation")
window.setFixedSize(450, 300)
window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Frameless and stays on top initially
window.setAttribute(Qt.WA_TranslucentBackground)  # Make window background transparent

# Layout and label for displaying images
layout = QVBoxLayout()
label = QLabel()
label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

# Set transparent background for the label
label.setAttribute(Qt.WA_TranslucentBackground)
label.setStyleSheet("background: transparent;")
layout.addWidget(label)
window.setLayout(layout)

# Folder containing the images in order
image_folder = "./img"
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
        # Move the window by the mouse offset
        new_pos = window.pos() + event.pos() - mouse_offset
        window.move(new_pos)

def mouseReleaseEvent(event: QMouseEvent):
    global dragging
    if event.button() == Qt.LeftButton:
        dragging = False

# Function to toggle the locked state when "Home" is pressed
def keyPressEvent(event: QKeyEvent):
    global locked
    if event.key() == Qt.Key_Home:
        locked = not locked
        if locked:
            # Lock the window (disable dragging and keep on top)
            window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            # Unlock the window (enable dragging)
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
