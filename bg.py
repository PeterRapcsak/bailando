import rembg
import numpy as np
from PIL import Image, ImageFilter
import os

# Folder containing the input images
input_folder = 'D:\\code\\bailando\\img'
output_folder = 'D:\\code\\bailando\\outp'

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process each image file in the folder
for count, filename in enumerate(sorted(os.listdir(input_folder)), start=1):
    # Load the input image
    input_image_path = os.path.join(input_folder, filename)
    input_image = Image.open(input_image_path).convert("RGBA")  # Ensure RGBA format

    # Convert the input image to a numpy array
    input_array = np.array(input_image)

    # Apply background removal with alpha matting
    output_array = rembg.remove(input_array, alpha_matting=True, alpha_matting_erode_size=15)

    # Convert output array back to an image and ensure correct color format
    output_image = Image.fromarray(output_array).convert("RGBA")

    # Save the output image with sequential naming
    output_image_path = os.path.join(output_folder, f"{count}.png")
    output_image.save(output_image_path)
    print(f"Processed {filename} -> Saved as {count}.png")
