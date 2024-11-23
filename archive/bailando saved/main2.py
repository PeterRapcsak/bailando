from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QPalette, QColor
from PySide6.QtCore import QTimer, Qt
import os
import sys

# Set up the main application window
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Image Animation")
window.setFixedSize(450, 300)
window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Frameless and stays on top
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

# Display the window and start the application
window.show()
sys.exit(app.exec())