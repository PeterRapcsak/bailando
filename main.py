from tkinter import Tk, Canvas, PhotoImage, NW
import os

# Set up the main application window
root = Tk()
root.attributes('-transparentcolor', '#f0f0f0')

# Canvas for displaying images
canvas = Canvas(root, width=450, height=300)
canvas.pack()

# Folder containing the images in order
image_folder = "./img"
image_files = sorted(
    [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.gif'))]
)

# Load all images and store them in a list
images = [PhotoImage(file=os.path.join(image_folder, img)) for img in image_files]

# Initialize index and display the first image
image_index = 0
image_on_canvas = canvas.create_image(0, 0, anchor=NW, image=images[image_index])

# Function to update the image every 0.07 seconds
def update_image():
    global image_index
    image_index = (image_index + 1) % len(images)  # Cycle through images
    canvas.itemconfig(image_on_canvas, image=images[image_index])
    root.after(30, update_image)  # Schedule the next image update

# Start the animation
update_image()

# Start the Tkinter main loop
root.mainloop()
